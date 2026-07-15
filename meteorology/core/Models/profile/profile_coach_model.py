from sqlalchemy import Column, String, Integer, func, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlite.database import Base
from meteorology.core.Models.profile.profile_enum import CooperationStatusForCoach



class ProfileCoach(Base):
    __tablename__="profile_coach"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    number_phone = Column(String(11), nullable=False, unique=True)
    email = Column(String(150), nullable=True, unique=True)
    bio = Column(String(200), nullable=True)
    work_history = Column(String(50), nullable=False)
    Documents_and_certificates = Column(String(500), nullable=False)
    area_of_activity = Column(String(200), nullable=False)
    Social_networks = Column(String(200), nullable=True)
    attendance_hours = Column(String(200), nullable=False)
    Cooperation_status = Column(Integer, default=CooperationStatusForCoach.yes.value ,nullable=False)

    specialty = relationship("Specialties", back_populates="coach")
    coach_to_athlete = relationship("CoachAthleteConnection", back_populates="coach")
    program = relationship("ProfileCoach", back_populates="coach")



class Specialties(Base):
    __tablename__="specialties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)
    specialties = Column(Integer, nullable=False)

    coach = relationship("ProfileCoach", back_populates="specialty")
