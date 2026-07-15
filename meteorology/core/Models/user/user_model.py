from sqlalchemy import Column, String, Integer, func, DateTime
from sqlalchemy.orm import Relationship
from sqlite.database import Base



class User(Base):
    __tablename__="user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(150), nullable=False, unique=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    number_phone = Column(String(11), nullable=False, unique=True)
    
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
