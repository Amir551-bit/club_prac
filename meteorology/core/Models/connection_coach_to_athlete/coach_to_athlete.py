from sqlalchemy import Column, String, Integer, func, Date, ForeignKey
from fastapi import Depends
from sqlalchemy.orm import relationship
from sqlite.database import Base
from core.Models.profile.profile_coach_model import ProfileCoach
from core.Models.profile.profile_athlete_model import ProfileAthlete
from datetime import date
from core.Models.connection_coach_to_athlete.coach_to_athlete_enum import ConnectionStatusEnum, CoachTypeEnum
from sqlalchemy.orm import Session
from core.execptions.execption import raise_not_found
from sqlite.database import get_db



class CoachAthleteConnection(Base):
    __tablename__="coach_athlete_connection"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_coach_id = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)
    profile_athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)
    start_date = Column(Date, default=func.now(), nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(Integer, nullable=False)
    manager_notes = Column(String(500), nullable=True)
    coach_role = Column(Integer, nullable=False)


    coach = relationship("ProfileCoach", back_populates="coach_to_athlete")
    athlete = relationship("ProfileAthlete", back_populates="coach_to_athlete")


    @classmethod
    def create(cls, db: Session, profile_coach_id: int, profile_athlete_id: int, start_date: date,status: ConnectionStatusEnum, 
               coach_role: CoachTypeEnum, manager_notes: str | None = None, end_date: date | None = None):
        
        instance = cls()
        instance.profile_coach_id = profile_coach_id
        instance.profile_athlete_id = profile_athlete_id
        instance.start_date = start_date
        instance.status = status.value
        instance.coach_role = coach_role.value
        instance.manager_notes = manager_notes
        instance.end_date = end_date
        return instance


    def update(self, start_date: date | None = None, status: ConnectionStatusEnum | None = None, coach_role: CoachTypeEnum | None = None, 
               manager_notes: str | None = None, end_date: date | None = None):

        self.start_date = start_date if start_date is not None else self.start_date
        self.manager_notes = manager_notes if manager_notes is not None else self.manager_notes
        self.end_date = end_date if end_date is not None else self.end_date
        if status is not None:
            self.status = status.value
        if coach_role is not None:
            self.coach_role = coach_role.value


    def change_coach(self, profile_coach_id: int):
        self.profile_coach_id = profile_coach_id

