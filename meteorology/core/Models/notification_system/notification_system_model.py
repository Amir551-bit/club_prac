from sqlalchemy import Column, String, Integer, func, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlite.database import Base
from datetime import date, datetime, timezone
from core.Models.notification_system.notification_system_enum import NotificationsRequiredEnum



class NotificationSystem(Base):
    __tablename__="notification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)
    title = Column(String(100), nullable=False)
    text = Column(String(500), nullable=False)
    type = Column(Integer, nullable=False)
    read_status = Column(Boolean, default=False, nullable=False)
    date_read = Column(DateTime, nullable=True)

    created_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    athlete = relationship("ProfileAthlete", back_populates="notifications")                


    @classmethod
    def create(cls, recipient: int, type: NotificationsRequiredEnum, title: str, text: str, read_status: bool):

        instance = cls()
        instance.recipient = recipient
        instance.title = title 
        instance.text = text
        instance.type = type.value
        instance.read_status = read_status
        return instance



    def read_notification(self):
        if self.read_status == False:
            self.read_status = True
            self.date_read = datetime.now(timezone.utc)