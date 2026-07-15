from sqlalchemy import Column, String, Integer, func, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlite.database import Base
from core.Models.profile.profile_coach_model import ProfileCoach
from core.Models.profile.profile_athlete_model import ProfileAthlete


class CoachAthleteConnection(Base):
    __tablename__="coach_athlete_connection"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_coach_id = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)
    profile_athlete_id = Column(Integer, ForeignKey("profile_athlete"), nullable=False)
    start_date = Column(Date, default=func.now(), nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(Integer, nullable=False)
    manager_notes = Column(String(500), nullable=True)
    coach_role = Column(Integer, nullable=False)


    coach = relationship("ProfileCoach", back_populates="coach_to_athlete")
    athlete = relationship("ProfileAthlete", back_populates="coach_to_athlete")