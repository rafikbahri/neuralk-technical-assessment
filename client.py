"""
Python client for the API implemented by `server.py`
"""
import time
import datetime

import polars as pl
import requests


HOST, PORT = "localhost", 8080


class NoResult(Exception):
    pass


class Client:
    """Client for the API exposed by server.py"""
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.url = f"http://{HOST}:{PORT}"

    def upload(self, file_path):
        """Upload a dataset and get its ID."""
        dataset_info = requests.get(f"{self.url}/upload").json()
        dataset_id = dataset_info["id"]
        with open(file_path, "rb") as f:
            requests.put(dataset_info["url"], f)
        return dataset_id

    def _wait(self, job_id, timeout):
        if timeout < 0.0:
            return
        start = time.monotonic()
        prev = None
        while True:
            status, since = self.status(job_id)
            if status != prev:
                if prev is not None:
                    print()
                prev = status
            if status in ["failed", "stopped", "canceled"]:
                print(status)
                raise NoResult(
                    f"Stopped waiting on job {job_id} with status: {status}"
                )
            if status == "finished":
                print(status)
                break
            print(f"{status: <10}{since:.1f}s", end="\r")
            if timeout is None:
                wait_for = 0.5
            else:
                wait_for = timeout - (time.monotonic() - start)
                if wait_for <= 0.0:
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
        fit_info = requests.post(f"{self.url}/fit", params={"id": dataset_id}).json()
        model_id = fit_info["id"]
        self._wait(model_id, timeout=timeout)
        return model_id

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

        predict_info = requests.post(
            f"{self.url}/predict",
            params={"dataset_id": dataset_id, "model_id": model_id},
        ).json()
        prediction_id = predict_info["id"]
        self._wait(prediction_id, timeout=timeout)
        return prediction_id

    def status(self, job_id):
        """
        Get the status of a `fit` or `predict` job

        Returns a pair (status string, timestamp when this status was reached).
        """
        info = requests.get(f"{self.url}/status", params={"id": job_id}).json()
        status = info["status"]
        now = datetime.datetime.now().timestamp()
        match status:
            case "started":
                return status, now - info["started_at"]
            case "finished" | "stopped" | "failed":
                return status, now - info["ended_at"]
            case _:
                return status, now - info["enqueued_at"]


    def download(self, result_id):
        """
        Download a prediction made by `predict`.

        result_id is the ID returned by `predict`.
        """
        result_url = requests.get(
            f"{self.url}/result", params={"id": result_id}
        ).json()["url"]
        with requests.get(result_url, stream=True) as resp:
            return pl.read_parquet(resp.raw)
