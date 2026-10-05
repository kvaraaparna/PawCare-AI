"""
PawCare AI – PostgreSQL Database Configuration
================================================
Initializes Flask-SQLAlchemy with PostgreSQL credentials
loaded from .env.

PostgreSQL is strictly required.
SQLite fallback is not allowed.
"""

import logging
import os

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger("PawCareAI.Database")


# ============================================================
# SQLALCHEMY INSTANCE
# ============================================================

db = SQLAlchemy()


# ============================================================
# GET DATABASE URL
# ============================================================

def get_database_url() -> str:
    """
    Get and validate the PostgreSQL database URL.
    """

    # First try DATABASE_URL from .env
    database_url = os.getenv("DATABASE_URL")

    # If DATABASE_URL is not provided,
    # build the URL from individual variables.
    if not database_url:

        user = os.getenv(
            "DB_USER",
            "postgres"
        )

        password = os.getenv(
            "DB_PASSWORD",
            "postgres"
        )

        host = os.getenv(
            "DB_HOST",
            "localhost"
        )

        port = os.getenv(
            "DB_PORT",
            "5432"
        )

        dbname = os.getenv(
            "DB_NAME",
            "dog_disease"
        )

        database_url = (
            f"postgresql+psycopg2://"
            f"{user}:{password}@"
            f"{host}:{port}/{dbname}"
        )

    # ========================================================
    # STRICT POSTGRESQL CHECK
    # ========================================================

    if not database_url.startswith("postgresql"):

        raise ValueError(
            "Invalid database dialect. "
            "PawCare AI requires PostgreSQL. "
            f"Received: {database_url}"
        )

    # ========================================================
    # ENSURE PSYCOPG2 DRIVER
    # ========================================================

    if database_url.startswith("postgresql://"):

        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg2://",
            1
        )

    return database_url


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_app(app):
    """
    Configure Flask-SQLAlchemy and bind it to the Flask app.
    """

    # Get PostgreSQL URL
    database_url = get_database_url()

    # Flask SQLAlchemy configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    app.config[
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    ] = False

    # Secret key
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "pawcare_ai_super_secret_key_2026_production"
    )

    # Connection pooling
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ========================================================
    # INITIALIZE SQLALCHEMY ONLY ONCE
    # ========================================================

    db.init_app(app)

    logger.info(
        "PostgreSQL database configured successfully."
    )