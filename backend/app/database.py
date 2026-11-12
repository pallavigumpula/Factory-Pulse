import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

logger = logging.getLogger("factorypulse.database")
logging.basicConfig(level=logging.INFO)

DATABASE_URL = settings.DATABASE_URL
IS_SQLITE = False

if os.getenv("TESTING", "").lower() == "true":
    DATABASE_URL = "sqlite:///./test_factorypulse.db"
    IS_SQLITE = True
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    try:
        if "mysql" in DATABASE_URL.lower():
            logger.info(f"Connecting to MySQL database at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}...")
            test_engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 3}
            )
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to MySQL database.")
            engine = test_engine
        else:
            IS_SQLITE = True
            engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    except Exception as exc:
        logger.warning("================================================================================")
        logger.warning("DATABASE CONNECTION NOTICE:")
        logger.warning(f"Could not connect to MySQL at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}.")
        logger.warning("Error details: %s", str(exc))
        logger.warning("To connect to MySQL 8:")
        logger.warning("  1. Start MySQL Server (e.g. net start mysql or through Windows Services).")
        logger.warning("  2. Create database: CREATE DATABASE factorypulse_db CHARACTER SET utf8mb4;")
        logger.warning("  3. Update MYSQL_USER and MYSQL_PASSWORD in .env or start.bat.")
        logger.warning("Falling back to local SQLite database: sqlite:///./factorypulse.db for seamless dev/testing.")
        logger.warning("================================================================================")
        IS_SQLITE = True
        DATABASE_URL = "sqlite:///./factorypulse.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
