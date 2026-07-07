import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace 'tarun' with whatever password you set during installation
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:tarun@localhost:5432/resume_screening"
)

# Note: Notice we changed username from 'ai_recruiter' to 'postgres' (the default Windows admin user)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()