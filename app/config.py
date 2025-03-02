import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-please-change-in-production")

    # Database configuration
    DB_HOST = os.environ.get("DB_HOST", "10.5.18.73")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME", "22CS30045")
    DB_USER = os.environ.get("DB_USER", "22CS30045")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "22CS30045")

    # App settings
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    DB_NAME = os.environ.get("DB_NAME", "22CS30045")


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    DB_NAME = os.environ.get("DB_NAME", "gram_panchayat_test")


class ProductionConfig(Config):
    """Production configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY")


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
