from sqlalchemy import Column, String, Integer, func, DateTime, ForeignKey, Text, Boolean
from fastapi import Depends
from sqlalchemy.orm import relationship
from sqlite.database import Base
from core.Models.profile.profile_coach_model import ProfileCoach
from core.Models.profile.profile_athlete_model import ProfileAthlete
from datetime import date, timezone, datetime
from core.Models.club_announcements_and_news.enum_file import NotificationType, LevelOfImportance, AudienceOfAnnouncement, AnnouncementStatus
from sqlalchemy.orm import Session
from core.execptions.execption import raise_not_found
from sqlite.database import get_db



class ClubAnnouncementsNews(Base):
    __tablename__="club_announcements_news"


    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    text = Column(Text, nullable=False)
    image = Column(String(100), nullable=False)
    notification_type = Column(Integer, nullable=False)
    importance = Column(Integer, nullable=False)
    audience = Column(Integer, nullable=False)
    publication_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    release_status = Column(Integer, nullable=False)
    author = Column(Integer, ForeignKey("user.id"), nullable=False)
    show_on_home_page = Column(Boolean, default=False)
    public_display = Column(Boolean, default=False)

    created_date = Column(DateTime, default=func.now())
    update_date = Column(DateTime, default=func.now(), server_onupdate=func.now())


    users = relationship("User", back_populates="announcement")


    @classmethod
    def create(cls, title: str, text: str, image: str, notification_type: NotificationType, importance: LevelOfImportance,
               audience: AudienceOfAnnouncement, publication_date: datetime, expiration_date: datetime, release_status: AnnouncementStatus,
               author: int, show_on_home_page: bool, public_display: bool):
        
        instance = cls()
        instance.title = title
        instance.text = text
        instance.image = image
        instance.notification_type = notification_type.value
        instance.importance = importance.value
        instance.audience = audience.value
        instance.publication_date = publication_date
        instance.expiration_date = expiration_date
        instance.release_status = release_status.value
        instance.author = author
        instance.show_on_home_page = show_on_home_page
        instance.public_display = public_display
        return instance


    def update(self, title: str | None = None, text: str | None = None, image: str | None = None,
               notification_type: NotificationType | None = None, importance: LevelOfImportance | None = None,
               audience: AudienceOfAnnouncement | None = None, publication_date: datetime | None = None, 
               expiration_date: datetime | None = None, release_status: AnnouncementStatus | None = None,
               show_on_home_page: bool | None = None, public_display: bool | None = None):

        self.title = title if title is not None else self.title
        self.text = text if text is not None else self.text
        self.image = image if image is not None else self.image
        self.publication_date = publication_date if publication_date is not None else self.publication_date
        self.expiration_date = expiration_date if expiration_date is not None else self.expiration_date
        self.show_on_home_page = show_on_home_page if show_on_home_page is not None else self.show_on_home_page
        self.public_display = public_display if public_display is not None else self.public_display
        if notification_type is not None:
            self.notification_type = notification_type.value
        if importance is not None:
            self.importance = importance.value
        if audience is not None:
            self.audience = audience.value
        if release_status is not None:
            self.release_status = release_status.value

