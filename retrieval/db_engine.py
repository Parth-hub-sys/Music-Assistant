import os
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine

load_dotenv()

def get_engine_for_chinook_db():
    """Create engine using PostgreSQL URL from environment."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not set in .env")
    
    return create_engine(database_url)

# Get the SQLAlchemy engine and initialize SQLDatabase utility
engine = get_engine_for_chinook_db()
db = SQLDatabase(engine)
