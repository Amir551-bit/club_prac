from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlite.database import Base



class UserRole(Base):
    __tablename__="user_role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    roles = relationship("Role", back_populates="user_roles")
    users = relationship("User", back_populates="user_roles")


    @classmethod
    def create(cls, role_id: int, user_id: int):
        instance = cls()
        instance.role_id = role_id
        instance.user_id = user_id
        return instance


    def update(self, role_id: int | None = None):
        self.role_id = role_id if role_id is not None else self.role_id

