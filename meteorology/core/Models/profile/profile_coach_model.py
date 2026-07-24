from sqlalchemy import Column, String, Integer, func, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlite.database import Base
from core.Models.profile.profile_enum import CooperationStatusForCoach
from core.Models.measurement_and_progress.progress_process import ProgressPicture
from core.Models.profile.profile_enum import CooperationStatusForCoach, SpecialtiesEnum


class ProfileCoach(Base):
    __tablename__="profile_coach"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    number_phone = Column(String(11), nullable=False, unique=True)
    email = Column(String(150), nullable=True, unique=True)
    bio = Column(String(200), nullable=True)
    work_history = Column(String(50), nullable=False)
    documents_and_certificates = Column(String(500), nullable=False)
    area_of_activity = Column(String(200), nullable=False)
    social_networks = Column(String(200), nullable=True)
    attendance_hours = Column(String(200), nullable=False)
    cooperation_status = Column(Integer, nullable=False)

    users = relationship("User", back_populates="coach")
    specialty = relationship("Specialties", back_populates="coach")
    coach_to_athlete = relationship("CoachAthleteConnection", back_populates="coach")
    program = relationship("ExerciseProgram", back_populates="coach")
    progress = relationship("ProgressProcess", back_populates="coach")
    picture_progress = relationship("ProgressPicture", back_populates="coach", foreign_keys=[ProgressPicture.data_recorder_coach])
    meal_plans = relationship("MealPlan", back_populates="coach")


    @classmethod
    def create(cls, user_id: int, first_name: str, last_name: str, number_phone: str, work_history: str, documents_and_certificates: str,
               area_of_activity: str, attendance_hours: str, cooperation_status: CooperationStatusForCoach,
                email: str | None = None, bio: str | None = None, social_networks: str | None = None):
        
        instance = cls()
        instance.user_id = user_id
        instance.first_name = first_name
        instance.last_name = last_name
        instance.number_phone = number_phone
        instance.work_history = work_history
        instance.documents_and_certificates = documents_and_certificates
        instance.area_of_activity = area_of_activity
        instance.attendance_hours = attendance_hours
        instance.cooperation_status = cooperation_status.value
        instance.email = email
        instance.bio = bio
        instance.social_networks = social_networks
        return instance
    

    def update(self, first_name: str | None = None, last_name: str | None = None, number_phone: str | None = None,
               work_history: str | None = None, documents_and_certificates: str | None = None, area_of_activity: str | None = None,
               attendance_hours: str | None = None, cooperation_status: CooperationStatusForCoach | None = None,
               email: str | None = None, bio: str | None = None, social_networks: str | None = None):
        
        self.first_name = first_name if first_name is not None else self.first_name
        self.last_name = last_name if last_name is not None else self.last_name
        self.number_phone = number_phone if number_phone is not None else self.number_phone
        self.work_history = work_history if work_history is not None else self.work_history
        self.documents_and_certificates = documents_and_certificates if documents_and_certificates is not None else self.documents_and_certificates
        self.area_of_activity = area_of_activity if area_of_activity is not None else self.area_of_activity
        self.attendance_hours = attendance_hours if attendance_hours is not None else self.attendance_hours
        self.email = email if email is not None else self.email
        self.bio = bio if bio is not None else self.bio
        self.social_networks = social_networks if social_networks is not None else self.social_networks
        if cooperation_status is not None:
            self.cooperation_status = cooperation_status.value

    

class Specialties(Base):
    __tablename__="specialties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)
    specialties = Column(Integer, nullable=False)

    coach = relationship("ProfileCoach", back_populates="specialty")


    @classmethod
    def create(cls, profile_id: int, specialties: SpecialtiesEnum):
        instance = cls()
        instance.profile_id = profile_id
        instance.specialties = specialties.value
        return instance
    
    def update(self, specialties: SpecialtiesEnum | None = None):
        if specialties is not None:
            self.specialties = specialties.value
