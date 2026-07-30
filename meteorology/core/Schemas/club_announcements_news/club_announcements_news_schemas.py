from pydantic import BaseModel, ConfigDict
from core.Models.club_announcements_and_news.enum_file import NotificationType, LevelOfImportance, AudienceOfAnnouncement, AnnouncementStatus
from datetime import date, datetime



class CreateClubAnnouncementsNew(BaseModel):
    title: str
    text : str
    image: str
    notification_type: NotificationType
    importance: LevelOfImportance
    audience: AudienceOfAnnouncement
    publication_date: datetime
    expiration_date: datetime
    release_status: AnnouncementStatus
    show_on_home_page: bool
    public_display: bool


class UpdateClubAnnouncementsNew(BaseModel):
    title: str | None = None
    text : str | None = None
    image: str | None = None
    notification_type: NotificationType | None = None
    importance: LevelOfImportance | None = None
    audience: AudienceOfAnnouncement | None = None
    publication_date: datetime | None = None
    expiration_date: datetime | None = None
    release_status: AnnouncementStatus | None = None
    show_on_home_page: bool | None = None
    public_display: bool | None = None




class ClubAnnouncementsNewResponse(BaseModel):
    title: str
    text : str
    image: str
    notification_type: NotificationType
    importance: LevelOfImportance
    audience: AudienceOfAnnouncement
    publication_date: datetime
    expiration_date: datetime
    release_status: AnnouncementStatus
    show_on_home_page: bool
    public_display: bool


    model_config = ConfigDict(from_attributes=True)

