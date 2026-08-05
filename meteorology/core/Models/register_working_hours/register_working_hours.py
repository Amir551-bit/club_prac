from sqlalchemy import Column, String, Integer, func, DateTime, Date, Text, Time
from sqlalchemy.orm import Session
from sqlite.database import Base
from datetime import date, time
from core.Models.register_working_hours.register_working_hours_enum import StatusOpenning
from core.execptions.execption import raise_bad_request



class RegisterWorkingHours(Base):
    __tablename__="register_working_hours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    day_date = Column(Date, server_default=func.current_date(), nullable=False)
    start_morning = Column(Time, nullable=False)
    stop_afternoon = Column(Time, nullable=False)
    start_afternoon = Column(Time, nullable=False)
    stop_night = Column(Time, nullable=False)
    status_openning = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=True)

    created_date = Column(DateTime, default=func.now())
    update_date = Column(DateTime, default=func.now(), server_onupdate=func.now())


    @classmethod
    def create(cls, day_date: date, start_morning: time, stop_afternoon: time, start_afternoon: time, stop_night: time, 
               status_openning: StatusOpenning, title: str, message: str | None = None):

        instance = cls()
        instance.day_date = day_date
        instance.start_morning = start_morning
        instance.stop_afternoon = stop_afternoon
        instance.start_afternoon = start_afternoon
        instance.stop_night = stop_night
        instance.status_openning = status_openning
        instance.title = title
        instance.message = message
        return instance


    def update(self, day_date: date | None = None, start_morning: time | None = None, stop_afternoon: time | None = None,
               start_afternoon: time | None = None, stop_night: time | None = None, status_openning: StatusOpenning | None = None, 
               title: str | None = None, message: str | None = None):

        now_date = func.current_date()
        if now_date > self.day_date:
            raise_bad_request("this is the past.")
        self.day_date = day_date if day_date is not None else self.day_date
        self.start_morning = start_morning if start_morning is not None else self.start_morning
        self.stop_afternoon = stop_afternoon if stop_afternoon is not None else self.stop_afternoon
        self.start_afternoon = start_afternoon if start_afternoon is not None else self.start_afternoon
        self.stop_night = stop_night if stop_night is not None else self.stop_night
        self.title = title if title is not None else self.title
        self.message = message if message is not None else self.message
        if status_openning is not None:
            self.status_openning = status_openning.value
        