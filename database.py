from sqlalchemy.orm import Session , sessionmaker
from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from utils.constants import DB_URL_FETCH_ERROR

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(DB_URL_FETCH_ERROR)

engine = create_engine(DATABASE_URL)
base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()