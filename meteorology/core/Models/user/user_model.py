from sqlalchemy import Column, String, Integer, func, DateTime
from sqlalchemy.orm import relationship
from sqlite.database import Base



class User(Base):
    __tablename__="user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(150), nullable=False, unique=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    number_phone = Column(String(10), nullable=False, unique=True)
    
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


    user_roles = relationship("UserRole", back_populates="users")
    coach = relationship("ProfileCoach", back_populates="users")
    athlete = relationship("ProfileAthlete", back_populates="users")


    @classmethod
    def create(cls, user_name: str, first_name: str, last_name: str, number_phone: str):
        instance = cls()
        instance.user_name = user_name
        instance.first_name = first_name
        instance.last_name = last_name
        instance.number_phone = number_phone
        return instance
    


    