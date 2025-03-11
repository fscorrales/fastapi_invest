__all__ = [
    "IOL_USERNAME",
    "IOL_PASSWORD",
    "MONGODB_URI",
    "MONGO_DB_NAME",
    "logger",
    "JWT_SECRET",
]

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Set environment variables
IOL_USERNAME = os.getenv("IOL_USERNAME", None)
IOL_PASSWORD = os.getenv("IOL_PASSWORD", None)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/invest")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "invest")


JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_key")

# HOST_URL = os.getenv("HOST_URL", "localhost")

# FRONTEND_HOST = os.getenv("FRONTEND_HOST", "localhost")

# HOST_PORT = int(os.getenv("HOST_PORT") or 8000)

# UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

# Fixing a "bycript issue"
logging.getLogger("passlib").setLevel(logging.ERROR)
