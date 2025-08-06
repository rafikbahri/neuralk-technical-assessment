"""
The 2 functions that perform the toy Machine-Learning (ML) tasks:

- `fit` fits a model and stores it.
- `predict` uses a fitted model to perform a prediction.
"""

import os
import io
import time

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
import polars as pl
import cloudpickle
import requests

import config
from logger import get_logger

logger = get_logger(__name__)

_TIMEOUT = float(os.environ.get("REQUEST_TIMEOUT", "3.05"))
os.environ["no_proxy"] = "*"


def _error_maybe():
    """Simulate random errors in the system."""
    rng = np.random.default_rng()
    if rng.binomial(n=1, p=0.05):
        logger.warning("Simulating a random error in the system")
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
    logger.info(f"Starting model training. Data URL: {data_url}")
    start_time = time.time()
    
    try:
        _error_maybe()
        
        logger.debug("Downloading training data")
        download_start = time.time()
        with requests.get(data_url, stream=True, timeout=_TIMEOUT) as resp:
            if resp.status_code != 200:
                logger.error(f"Failed to download training data. Status code: {resp.status_code}")
                raise RuntimeError(f"Failed to download training data: {resp.status_code}")
            df = pl.read_parquet(resp.raw)
        download_time = time.time() - download_start
        logger.debug(f"Downloaded training data in {download_time:.2f}s. Shape: {df.shape}")
        
        if "y" not in df.columns:
            logger.error("Training data missing required 'y' column")
            raise ValueError("Training data must contain a 'y' column with target values")
            
        logger.debug("Starting model training")
        train_start = time.time()
        X, y = df.drop("y"), df["y"]
        model = HistGradientBoostingClassifier().fit(X, y)
        train_time = time.time() - train_start
        logger.debug(f"Model training completed in {train_time:.2f}s")
        
        logger.debug("Uploading trained model")
        upload_start = time.time()
        model_data = cloudpickle.dumps(model)
        requests.put(model_url, data=model_data, timeout=_TIMEOUT)
        upload_time = time.time() - upload_start
        logger.debug(f"Model uploaded in {upload_time:.2f}s. Size: {len(model_data)} bytes")
        
        total_time = time.time() - start_time
        logger.info(f"Model training completed successfully in {total_time:.2f}s")
    
    except Exception as e:
        logger.error(f"Model training failed: {type(e).__name__}: {e}", exc_info=True)
        raise


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
    logger.info(f"Starting prediction. Data URL: {data_url}, Model URL: {model_url}")
    start_time = time.time()
    
    try:
        _error_maybe()
        
        logger.debug("Downloading test data")
        data_start = time.time()
        with requests.get(data_url, stream=True, timeout=_TIMEOUT) as resp:
            if resp.status_code != 200:
                logger.error(f"Failed to download test data. Status code: {resp.status_code}")
                raise RuntimeError(f"Failed to download test data: {resp.status_code}")
            df = pl.read_parquet(resp.raw)
        data_time = time.time() - data_start
        logger.debug(f"Downloaded test data in {data_time:.2f}s. Shape: {df.shape}")
        
        logger.debug("Downloading model")
        model_start = time.time()
        with requests.get(model_url, stream=True, timeout=_TIMEOUT) as resp:
            if resp.status_code != 200:
                logger.error(f"Failed to download model. Status code: {resp.status_code}")
                raise RuntimeError(f"Failed to download model: {resp.status_code}")
            model = cloudpickle.load(resp.raw)
        model_time = time.time() - model_start
        logger.debug(f"Downloaded model in {model_time:.2f}s")
        
        logger.debug("Making predictions")
        predict_start = time.time()
        
        # Handle the case where 'y' might be in the test data (validation case)
        # but not required for prediction
        try:
            input_data = df.drop("y", strict=False)
        except Exception as e:
            logger.error(f"Error preparing test data: {e}")
            raise
            
        pred = model.predict(input_data)
        pred = pl.DataFrame({"y": pred})
        predict_time = time.time() - predict_start
        logger.debug(f"Made predictions in {predict_time:.2f}s for {len(pred)} samples")
        
        logger.debug("Uploading prediction results")
        upload_start = time.time()
        buf = io.BytesIO()
        pred.write_parquet(buf)
        result_data = buf.getvalue()
        response = requests.put(result_url, data=result_data, timeout=_TIMEOUT)
        if response.status_code != 200:
            logger.error(f"Failed to upload results. Status code: {response.status_code}")
            raise RuntimeError(f"Failed to upload results: {response.status_code}")
        upload_time = time.time() - upload_start
        logger.debug(f"Uploaded results in {upload_time:.2f}s. Size: {len(result_data)} bytes")
        
        total_time = time.time() - start_time
        logger.info(f"Prediction completed successfully in {total_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Prediction failed: {type(e).__name__}: {e}", exc_info=True)
        raise
