import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing. Check your .env file.")
engine = create_engine(
    database_url, pool_pre_ping=True, connect_args={"connect_timeout": 5}
)