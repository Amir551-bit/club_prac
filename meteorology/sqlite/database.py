from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlite.config import setting


engine = create_engine(setting.SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False})

Sessionlocal = sessionmaker(autocommit=False, bind=engine)


Base = declarative_base()


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()