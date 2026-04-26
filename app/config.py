import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    SOURCE_DREMIO_URL = os.getenv("SOURCE_DREMIO_URL", "")
    SOURCE_DREMIO_PAT = os.getenv("SOURCE_DREMIO_PAT", "")
    SOURCE_DREMIO_USERNAME = os.getenv("SOURCE_DREMIO_USERNAME", "")
    SOURCE_DREMIO_PASSWORD = os.getenv("SOURCE_DREMIO_PASSWORD", "")

    TARGET_DREMIO_URL = os.getenv("TARGET_DREMIO_URL", "")
    TARGET_DREMIO_PAT = os.getenv("TARGET_DREMIO_PAT", "")
    TARGET_DREMIO_USERNAME = os.getenv("TARGET_DREMIO_USERNAME", "")
    TARGET_DREMIO_PASSWORD = os.getenv("TARGET_DREMIO_PASSWORD", "")
