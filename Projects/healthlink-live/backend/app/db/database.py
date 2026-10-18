import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine


from app.core.config import PROJECT_ROOT
from app.core import config

database_url = config.DATABASE_URL

if not database_url:
    raise RuntimeError("DATABASE_URL is missing. Check your .env file.")
engine = create_engine(
    database_url, pool_pre_ping=True, connect_args={"connect_timeout": 5}
)