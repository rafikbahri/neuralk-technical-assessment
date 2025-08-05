"""
The 2 functions that perform the toy Machine-Learning (ML) tasks:

- `fit` fits a model and stores it.
- `predict` uses a fitted model to perform a prediction.
"""

import os
import io

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
import polars as pl
import cloudpickle
import requests

_TIMEOUT = 3.05
os.environ["no_proxy"] = "*"


def _error_maybe():
    """Simulate random errors in the system."""
    rng = np.random.default_rng()
    if rng.binomial(n=1, p=0.05):
        raise RuntimeError("Something unexpected went wrong")


def fit(data_url, model_url):
    """
    Fit a gradient boosting model.

    Parameters
    ----------
    data_url : str
        url from which the training data can be downloaded as a parquet file.
        It must have a column named 'y' that contains the targets.
    model_url : str
        url where the serialized model can be uploaded (as a cloudpickle file).
    """
    _error_maybe()
    with requests.get(data_url, stream=True, timeout=_TIMEOUT) as resp:
        df = pl.read_parquet(resp.raw)
    X, y = df.drop("y"), df["y"]
    model = HistGradientBoostingClassifier().fit(X, y)
    requests.put(model_url, data=cloudpickle.dumps(model), timeout=_TIMEOUT)


def predict(data_url, model_url, result_url):
    """
    Make a prediction with a fitted model.

    Parameters
    ----------
    data_url : str
        url from which the unseen (test) data, for which predictions must be
        made, can be downloaded as a parquet file.
    model_url : str
        url where the serialized model can be downloaded (as a cloudpickle
        file).
    result_url : str
        url where the predictions can be uploaded. It will be a parquet file
        with a single column named 'y'.
    """
    _error_maybe()
    with requests.get(data_url, stream=True, timeout=_TIMEOUT) as resp:
        df = pl.read_parquet(resp.raw)
    with requests.get(model_url, stream=True, timeout=_TIMEOUT) as resp:
        model = cloudpickle.load(resp.raw)
    pred = model.predict(df.drop("y", strict=False))
    pred = pl.DataFrame({"y": pred})
    buf = io.BytesIO()
    pred.write_parquet(buf)
    requests.put(result_url, data=buf.getvalue(), timeout=_TIMEOUT)
