from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    "sqlite:///parking_lot.db",
)

Session = sessionmaker(bind=engine, autoflush=False)
session = Session()

Base = declarative_base()
