from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlite.database import Base
from core.Models.role.permission import Permission



class Role(Base):
    __tablename__="role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    permission = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)


    user_roles = relationship("UserRole", back_populates="roles", cascade="all, delete-orphan")

    def has_permission(self, permission: Permission) -> bool:

        return (self.permission & permission) == permission  
    


    