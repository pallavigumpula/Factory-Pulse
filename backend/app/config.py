import os
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file if present
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

class Settings:
    PROJECT_NAME: str = "FactoryPulse"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "factorypulse_db")
    
    # Priority: explicit DATABASE_URL > MySQL > SQLite fallback
    DEFAULT_MYSQL_URL: str = (
    f"mysql+pymysql://{quote_plus(MYSQL_USER)}:"
    f"{quote_plus(MYSQL_PASSWORD)}@"
    f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
)
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_MYSQL_URL)
    
    # Security / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "factorypulse_super_secret_jwt_key_2026_hackathon")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # Seed
    RANDOM_SEED: int = 20261022

settings = Settings()
