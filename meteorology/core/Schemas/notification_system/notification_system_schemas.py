from pydantic import BaseModel, ConfigDict
from core.Models.notification_system.notification_system_enum import NotificationsRequiredEnum
from datetime import date, datetime
from core.Schemas.profile.profile_athlete import ProfileAthleteResponse


class CreateNotification(BaseModel):
    
    title: str
    text: str
    type: NotificationsRequiredEnum
    read_status: bool



class NotificationResponse(BaseModel):

    recipient: int
    title: str
    text: str
    type: NotificationsRequiredEnum
    read_status: bool
    date_read: datetime | None = None
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)



class NotificationResponses(BaseModel):

    items: list[NotificationResponse]
    total: int
    limit: int
    offset: int
    profile_athlete: ProfileAthleteResponse
