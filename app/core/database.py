from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We get the URL from the .env file.
# Note: we use psycopg2 as the driver, so the URL should start with `postgresql+psycopg2://`
# Although, `postgresql://` often defaults to psycopg2.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://test:test@localhost:5432/green_ledger_db"
)

# The engine is the core interface to the database.
# echo=True means it will print all SQL commands it runs
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# SessionLocal class is a factory for new Session objects.
# A session is an active transaction window to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 2.0 Modern approach: Subclass from DeclarativeBase
class Base(DeclarativeBase):
    pass

# Dependency to get the database session in our FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
