"""
Python client for the API implemented by `server.py`
"""
import time
import datetime

import polars as pl
import requests

import config
from logger import get_logger

logger = get_logger(__name__)


class NoResult(Exception):
    pass


class Client:
    """Client for the API exposed by server.py"""
    def __init__(self, host=None, port=None):
        self.host = host or config.SERVER_HOST
        self.port = port or config.SERVER_PORT
        self.url = f"http://{self.host}:{self.port}"
        logger.debug(f"Client initialized with URL: {self.url}")

    def upload(self, file_path):
        """Upload a dataset and get its ID."""
        logger.info(f"Uploading dataset: {file_path}")
        try:
            dataset_info = requests.get(f"{self.url}/upload").json()
            dataset_id = dataset_info["id"]
            logger.debug(f"Got upload URL and ID: {dataset_id}")
            
            with open(file_path, "rb") as f:
                response = requests.put(dataset_info["url"], f)
                response.raise_for_status()
                
            logger.info(f"Dataset uploaded successfully. ID: {dataset_id}")
            return dataset_id
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error uploading dataset: {str(e)}")
            raise

    def _wait(self, job_id, timeout):
        if timeout < 0.0:
            return
            
        logger.debug(f"Waiting for job {job_id} with timeout: {timeout}")
        start = time.monotonic()
        prev = None
        
        while True:
            status, since = self.status(job_id)
            
            # Log status changes
            if status != prev:
                if prev is not None:
                    logger.info(f"Job {job_id} status changed: {prev} → {status}")
                else:
                    logger.info(f"Job {job_id} status: {status}")
                prev = status
                
            # Handle terminal states
            if status in ["failed", "stopped", "canceled"]:
                logger.error(f"Job {job_id} {status} after {since:.1f}s")
                raise NoResult(f"Stopped waiting on job {job_id} with status: {status}")
                
            if status == "finished":
                logger.info(f"Job {job_id} finished successfully after {since:.1f}s")
                break
                
            # Progress update
            if int(since) % 5 == 0:  # Log only every 5 seconds to avoid excessive logging
                logger.debug(f"Job {job_id} still {status} after {since:.1f}s")
            
            # Terminal update for user feedback
            print(f"{status: <10}{since:.1f}s", end="\r")
            
            # Handle timeout
            if timeout is None:
                wait_for = 0.5
            else:
                wait_for = timeout - (time.monotonic() - start)
                if wait_for <= 0.0:
                    logger.warning(f"Job {job_id} timed out after {timeout}s")
                    raise TimeoutError(f"Timed out waiting for job {job_id}")
                wait_for = min(wait_for, 0.5)
                
            time.sleep(wait_for)

    def fit(self, dataset_id, timeout=-1):
        """
        Start fitting a model and return the corresponding job ID.

        Parameters
        ----------
        dataset_id : str
            An ID returned by `upload`. The dataset to use to fit the model.
        timeout : float
            If < 0:  launch the job and return immediately
            If None: launch the job and wait until the job is finished. Raise
                     a NoResult exception if the job failed.
            If >= 0: Same as when timeout=None, but raise a TimeoutError if the
                     job has not fninised after `timeout` seconds.
        """
        logger.info(f"Starting model training with dataset ID: {dataset_id}")
        try:
            fit_info = requests.post(f"{self.url}/fit", params={"id": dataset_id}).json()
            model_id = fit_info["id"]
            logger.debug(f"Model training job created with ID: {model_id}")
            
            self._wait(model_id, timeout=timeout)
            return model_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Error requesting model training: {str(e)}")
            raise

    def predict(self, dataset_id, model_id, timeout=-1):
        """
        Start a prediction and return the corresponding job ID.

        Parameters
        ----------
        dataset_id : str
            An ID returned by `upload`. The dataset for which to make predictions.
        model_id : str
            An ID returned by `fit`. The model that makes the prediction.
        timeout : float
            If < 0:  launch the job and return immediately
            If None: launch the job and wait until the job is finished. Raise
                     a NoResult exception if the job failed.
            If >= 0: Same as when timeout=None, but raise a TimeoutError if the
                     job has not fninised after `timeout` seconds.
        """
        logger.info(f"Starting prediction with dataset ID: {dataset_id} and model ID: {model_id}")
        try:
            predict_info = requests.post(
                f"{self.url}/predict",
                params={"dataset_id": dataset_id, "model_id": model_id},
            ).json()
            prediction_id = predict_info["id"]
            logger.debug(f"Prediction job created with ID: {prediction_id}")
            
            self._wait(prediction_id, timeout=timeout)
            return prediction_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Error requesting prediction: {str(e)}")
            raise

    def status(self, job_id):
        """
        Get the status of a `fit` or `predict` job

        Returns a pair (status string, timestamp when this status was reached).
        """
        try:
            info = requests.get(f"{self.url}/status", params={"id": job_id}).json()
            status = info["status"]
            now = datetime.datetime.now().timestamp()
            
            elapsed = 0
            match status:
                case "started":
                    elapsed = now - info["started_at"]
                case "finished" | "stopped" | "failed":
                    elapsed = now - info["ended_at"]
                case _:
                    elapsed = now - info["enqueued_at"]
            
            logger.debug(f"Job {job_id} status: {status}, elapsed: {elapsed:.1f}s")
            return status, elapsed
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching status for job {job_id}: {str(e)}")
            raise


    def download(self, result_id):
        """
        Download a prediction made by `predict`.

        result_id is the ID returned by `predict`.
        """
        logger.info(f"Downloading prediction results for ID: {result_id}")
        try:
            # Get the download Presigned URL
            result_url_response = requests.get(
                f"{self.url}/result", params={"id": result_id}
            )
            result_url_response.raise_for_status()
            result_url = result_url_response.json()["url"]
            
            logger.debug(f"Got result download URL for ID: {result_id}")
            
            # Download the actual result
            with requests.get(result_url, stream=True) as resp:
                resp.raise_for_status()
                data = pl.read_parquet(resp.raw)
                
            logger.info(f"Successfully downloaded prediction results. Shape: {data.shape}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading prediction results: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing downloaded prediction data: {type(e).__name__}: {str(e)}")
            raise
