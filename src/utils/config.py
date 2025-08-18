"""
Environment configuration for the Neuralk API service.
Loads configuration from .env files and provides access to environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".env.local"), override=True)

# Server configuration
SERVER_HOST = os.environ.get("SERVER_HOST", "localhost")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# MinIO configuration
MINIO_HOST = os.environ.get("MINIO_HOST", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "False").lower() == "true"

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Job configuration
JOB_TIMEOUT = os.environ.get("JOB_TIMEOUT", "600s")
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "4"))

# Queue name
QUEUE_NAME = os.environ.get("QUEUE_NAME", "default")

# Proxy to the Minio docker container - needed for client to use presigned URLs
MINIO_PROXY_ADDRESS = os.environ.get("MINIO_PROXY_ADDRESS", "localhost")
MINIO_PROXY_PORT = int(os.environ.get("MINIO_PROXY_PORT", "9002"))

def get_redis_connection():
    """Returns a configured Redis connection"""
    from redis import Redis
    
    return Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=False
    )

def get_minio_client():
    """Returns a configured MinIO client"""
    import minio
    
    return minio.Minio(
        MINIO_HOST,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )
