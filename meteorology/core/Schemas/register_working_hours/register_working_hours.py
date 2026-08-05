from pydantic import BaseModel, ConfigDict
from core.Models.register_working_hours.register_working_hours_enum import StatusOpenning
from datetime import date, datetime, time



class CreateRegisterWorkingHours(BaseModel):
    day_date: date
    start_morning: time
    stop_afternoon: time
    start_afternoon: time
    stop_night: time
    status_openning: StatusOpenning
    title: str
    message: str | None = None


class UpdateRegisterWorkingHours(BaseModel):
    day_date: date | None = None
    start_morning: time | None = None
    stop_afternoon: time | None = None
    start_afternoon: time | None = None
    stop_night: time | None = None
    status_openning: StatusOpenning | None = None
    title: str | None = None
    message: str | None = None



class RegisterWorkingHoursResponse(BaseModel):
    day_date: date
    start_morning: time
    stop_afternoon: time
    start_afternoon: time
    stop_night: time
    status_openning: StatusOpenning
    title: str
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)