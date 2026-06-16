"""Database utility functions"""

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.utils.config import get_settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def get_sqlalchemy_engine():
    """Get SQLAlchemy engine"""
    settings = get_settings()
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Test connection before using
        echo=settings.DEBUG,
    )
    return engine


def get_session_factory():
    """Get SQLAlchemy session factory"""
    engine = get_sqlalchemy_engine()
    return sessionmaker(bind=engine)


def get_psycopg2_connection():
    """Get psycopg2 database connection"""
    settings = get_settings()
    try:
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
        )
        logger.info(f"Connected to database: {settings.DB_NAME}")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def execute_sql_file(filepath: str, conn=None) -> None:
    """Execute SQL file against database

    Args:
        filepath: Path to SQL file
        conn: psycopg2 connection. If None, creates new connection
    """
    close_conn = False
    if conn is None:
        conn = get_psycopg2_connection()
        close_conn = True

    try:
        with open(filepath, "r") as f:
            sql_script = f.read()

        cursor = conn.cursor()
        cursor.execute(sql_script)
        conn.commit()
        logger.info(f"Successfully executed SQL file: {filepath}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error executing SQL file {filepath}: {e}")
        raise
    finally:
        if close_conn:
            conn.close()
