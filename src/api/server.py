"""
Toy server to mimick a neuralk-like API.
It can be used like this:

GET /upload
    Returns an ID for the dataset, and a presigned url where it can be uploaded
    as a parquet file.
POST /fit?id=<dataset ID>
    Start training a model on the dataset identified by `id` (an ID returned by
    `/upload`). Returns an ID used to refer to the training task and resulting
    model.
POST /predict?dataset_id=<dataset ID>&model_id=<model ID>
    Start a prediction using the trained model identified by `model_id` (an ID
    returned by `/fit`) with as input the dataset identified by `dataset_id`
    (an ID returned by `/upload`).
GET /status?id=<fit or predict ID>
    Status of the (`fit` or `predict`) task & timestamps for when it was
    enqueued, started, and finished.
GET /result?id=<predict ID>
    Returns a presigned url from which the prediction result parquet file can
    be downloaded. `id` is an ID returned by `/predict`.

NOTE: currently the server binds to localhost and uses the default connection
options for Redis (localhost:6379) and MinIO (localhost:9000), which you may
need to modify (see the end of the file).
"""

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import uuid

from rq import Queue, Retry
from rq.job import Job

import src.utils.config as config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Handler(BaseHTTPRequestHandler):

    error_message_format = "%(code)d %(message)s\n"
    
    def log_message(self, format, *args):
        """Override the default log_message to use our logger"""
        logger.info("%s - %s" % (self.address_string(), format % args))

    def __send_response(self, msg):
        msg = msg.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(len(msg)))
        self.end_headers()
        self.wfile.write(msg)

    def do_GET(self):
        self.__handle()

    def do_POST(self):
        self.__handle()

    def __handle(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        task = parsed.path.rstrip("/").split("/")[-1].replace("-", "_")
        try:
            method = getattr(self, f"_do_{self.command}_{task}")
        except AttributeError:
            self.send_error(HTTPStatus.BAD_REQUEST, f"Bad request: {task}")
            return
        try:
            method(query)
        except Exception as e:
            logger.error(f"Error processing request: {type(e).__name__}: {e}", exc_info=True)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Error")

    def _do_GET_upload(self, query):
        del query
        id = str(uuid.uuid4())
        url = MINIO.get_presigned_url("PUT", "datasets", id)
        logger.info(f"Dataset upload requested. Generated ID: {id}")
        self.__send_response(json.dumps({"url": url, "id": id}))

    def _do_GET_status(self, query):
        id = query["id"][0]
        job = Job.fetch(id, connection=REDIS)

        def ts(datetime):
            return None if datetime is None else datetime.timestamp()

        self.__send_response(
            json.dumps(
                {
                    "status": job.get_status(),
                    "enqueued_at": ts(job.enqueued_at),
                    "started_at": ts(job.started_at),
                    "ended_at": ts(job.ended_at),
                }
            )
        )

    def _do_GET_result(self, query):
        predict_id = query["id"][0]
        job = Job.fetch(predict_id, connection=REDIS)
        if (status := job.get_status()) != "finished":
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                f"Cannot get result of job with status {status}",
            )
            return
        url = MINIO.get_presigned_url("GET", "results", predict_id)
        self.__send_response(json.dumps({"url": url}))

    def _do_POST_fit(self, query):
        data_id = query["id"][0]
        data_url = MINIO.get_presigned_url("GET", "datasets", data_id)
        model_id = str(uuid.uuid4())
        model_url = MINIO.get_presigned_url("PUT", "models", model_id)
        logger.info(f"Model training requested. Dataset ID: {data_id}, Model ID: {model_id}")
        QUEUE.enqueue(
            "ml.fit",
            args=(data_url, model_url),
            job_timeout=config.JOB_TIMEOUT,
            job_id=model_id,
            retry=Retry(max=config.MAX_RETRIES),
        )
        logger.debug(f"Fit job enqueued with ID: {model_id}")
        self.__send_response(json.dumps({"id": model_id}))

    def _do_POST_predict(self, query):
        data_id = query["dataset_id"][0]
        data_url = MINIO.get_presigned_url("GET", "datasets", data_id)
        model_id = query["model_id"][0]
        model_url = MINIO.get_presigned_url("GET", "models", model_id)
        result_id = str(uuid.uuid4())
        result_url = MINIO.get_presigned_url("PUT", "results", result_id)
        logger.info(f"Prediction requested. Dataset ID: {data_id}, Model ID: {model_id}, Result ID: {result_id}")
        QUEUE.enqueue(
            "ml.predict",
            args=(data_url, model_url, result_url),
            job_timeout=config.JOB_TIMEOUT,
            job_id=result_id,
            retry=Retry(max=config.MAX_RETRIES),
        )
        logger.debug(f"Predict job enqueued with ID: {result_id}")
        self.__send_response(json.dumps({"id": result_id}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=config.SERVER_PORT)
    args = parser.parse_args()

    HOST, PORT = config.SERVER_HOST, config.SERVER_PORT or args.port
    
    # Get MinIO client from config
    MINIO = config.get_minio_client()
    
    all_buckets = [bucket.name for bucket in MINIO.list_buckets()]
    for bucket in ["datasets", "models", "results"]:
        if bucket not in all_buckets:
            logger.info(f"Creating bucket: {bucket}")
            MINIO.make_bucket(bucket)

    REDIS = config.get_redis_connection()
    QUEUE = Queue(config.QUEUE_NAME, connection=REDIS)

    logger.info(f"Server starting at {HOST}:{PORT}")

    with ThreadingHTTPServer((HOST, PORT), Handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
