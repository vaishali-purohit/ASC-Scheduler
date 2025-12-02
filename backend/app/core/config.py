import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    # Database configuration from .env
    DB_USERNAME: str = os.getenv("DB_USERNAME", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOSTNAME: str = os.getenv("DB_HOSTNAME", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "asc_scheduler")

    # URL-encode the password
    DB_PASSWORD_ENCODED: str = quote_plus(DB_PASSWORD)
    
    # Construct DATABASE_URL for psycopg2
    DATABASE_URL: str = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD_ENCODED}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"

settings = Settings()
