"""
PawCare AI – PostgreSQL Database Initialization Command
========================================================
Usage:
    python init_db.py

Functionality:
1. Connects to PostgreSQL server.
2. Checks if 'pawcare_ai' database exists; creates it safely if missing.
3. Initializes Flask-SQLAlchemy application context.
4. Executes db.create_all() to safely create any missing tables
   WITHOUT dropping, deleting, or altering existing data.
5. Seeds baseline production model (ResNet-18 v1, 76.06% test accuracy)
   into 'model_versions' if not already present.
6. Displays a summary of verified tables and active model version.
"""

import logging
import sys
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv
from flask import Flask
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment configuration
load_dotenv()

from database import db, get_database_url, init_app
from models import ModelVersion

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
)
logger = logging.getLogger("PawCareAI.InitDB")


def ensure_database_exists(database_url: str):
    """
    Connects to PostgreSQL administrative database ('postgres') and
    creates 'pawcare_ai' if it does not already exist.
    """
    parsed = urlparse(database_url)
    target_dbname = parsed.path.lstrip("/") or "pawcare_ai"
    user = parsed.username or "postgres"
    password = parsed.password or ""
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432

    logger.info(f"Checking PostgreSQL server at {host}:{port} for database '{target_dbname}'...")

    try:
        # Connect to default 'postgres' maintenance database
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=5
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if target database already exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_dbname,))
        exists = cursor.fetchone()

        if not exists:
            logger.info(f"Database '{target_dbname}' not found. Creating database...")
            # Database identifiers cannot be parameterized in SQL statements
            cursor.execute(f'CREATE DATABASE "{target_dbname}";')
            logger.info(f"Database '{target_dbname}' successfully created!")
        else:
            logger.info(f"Database '{target_dbname}' already exists.")

        cursor.close()
        conn.close()
    except psycopg2.OperationalError as e:
        logger.error(
            f"Failed to connect to PostgreSQL server: {e}\n"
            f"Please verify that PostgreSQL is running and check credentials in .env."
        )
        raise


def seed_baseline_model():
    """
    Seeds the current baseline model weights (ResNet18 v1, 76.06% accuracy)
    into 'model_versions' if not already registered.
    """
    existing_model = ModelVersion.query.filter_by(
        model_name="ResNet18",
        model_version="v1"
    ).first()

    if not existing_model:
        logger.info("Seeding baseline model (ResNet18 v1) into 'model_versions' table...")
        baseline = ModelVersion(
            model_name="ResNet18",
            model_version="v1",
            model_path="best_dog_disease_resnet18.pth",
            accuracy=76.06,
            description="Initial baseline production ResNet-18 model for canine skin disease classification.",
            is_active=True
        )
        db.session.add(baseline)
        db.session.commit()
        logger.info("Baseline model record successfully seeded: ResNet18 v1 (Accuracy: 76.06%).")
    else:
        logger.info(
            f"Baseline model already registered: id={existing_model.id} "
            f"({existing_model.model_name} {existing_model.model_version}, Accuracy: {existing_model.accuracy}%)."
        )


def main():
    """Main database initialization entry point."""
    print("=" * 65)
    print("PAWCARE AI – POSTGRESQL DATABASE INITIALIZATION")
    print("=" * 65)

    # 1. Resolve and validate database URL
    try:
        db_url = get_database_url()
    except Exception as e:  # noqa: BLE001
        logger.critical(f"Configuration error: {e}")
        sys.exit(1)

    # 2. Ensure target database exists on PostgreSQL server
    try:
        ensure_database_exists(db_url)
    except Exception as e:  # noqa: BLE001
        logger.critical(f"Database creation aborted: {e}")
        sys.exit(1)

    # 3. Create Flask application context and bind SQLAlchemy
    app = Flask(__name__)
    init_app(app)

    with app.app_context():
        # 4. Safe table creation (does NOT delete existing tables or records)
        logger.info("Creating missing tables via SQLAlchemy db.create_all()...")
        db.create_all()
        logger.info("All table schemas verified successfully.")

        # 5. Seed baseline production model record
        seed_baseline_model()

        # 6. Verify tables in information_schema
        inspector = db.inspect(db.engine)
        created_tables = inspector.get_table_names()

        print("\n" + "=" * 65)
        print("DATABASE INITIALIZATION SUMMARY:")
        print(f"Target Database: {inspector.engine.url.database}")
        print(f"Dialect:         {inspector.engine.dialect.name} (PostgreSQL)")
        print(f"Total Tables:    {len(created_tables)}")
        print("-" * 65)
        for i, tbl in enumerate(created_tables, 1):
            columns = [col["name"] for col in inspector.get_columns(tbl)]
            print(f"  {i}. {tbl:<20} ({len(columns)} columns: {', '.join(columns[:4])}...)")
        print("=" * 65)
        print(">>> SUCCESS: PostgreSQL database 'pawcare_ai' initialized successfully!\n")


if __name__ == "__main__":
    main()
