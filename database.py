import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


SQLALCHEMY_DATABASE_URL = (
    os.environ.get('DATABASE_URL', 'postgresql:///invoice-app'))

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)