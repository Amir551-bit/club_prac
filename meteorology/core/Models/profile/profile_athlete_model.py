from sqlalchemy import Column, String, Integer, func, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlite.database import Base
from core.Models.profile.profile_enum import MembershipStatusForAthlete
from core.Models.measurement_and_progress.progress_process import ProgressPicture
from core.Models.profile.profile_enum import Gender, MembershipStatusForAthlete, MainGoal
from datetime import date

class ProfileAthlete(Base):
    __tablename__="profile_athlete"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    number_phone = Column(String(11), nullable=False, unique=True)
    email = Column(String(150), nullable=True, unique=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Integer, nullable=False)
    height = Column(String(50), nullable=False)
    initial_weight = Column(String(50), nullable=False)
    training_goal = Column(String(1000), nullable=True)
    date_of_membership = Column(Date, nullable=False)
    membership_status = Column(Integer, nullable=False)
    the_main_trainer = Column(String(150), nullable=False)
    management_description = Column(String(1500), nullable=True)
    emergency_contact_number_if_needed = Column(String(11), nullable=True)


    users = relationship("User", back_populates="athlete")
    sports_info = relationship("AthleteSportsInfo", back_populates="athlete")
    coach_to_athlete = relationship("CoachAthleteConnection", back_populates="athlete")
    program = relationship("ExerciseProgram", back_populates="athlete")
    regis_daily_practice = relationship("RegistrationDailyPractice", back_populates="athlete")
    progress = relationship("ProgressProcess", back_populates="athlete")
    picture_progress = relationship(
        "ProgressPicture", 
        back_populates="athlete", 
        foreign_keys="[ProgressPicture.data_recorder_athlete]"
    )

    @classmethod
    def create(cls, user_id: int, first_name: str, last_name: str, number_phone: str,
               date_of_birth: date, gender: Gender, height: str, initial_weight: str,
               date_of_membership: date, membership_status: MembershipStatusForAthlete,
               the_main_trainer: str, management_description: str | None = None, training_goal: str | None = None,
               email: str | None = None, emergency_contact_number_if_needed: str | None = None):

        instance = cls()
        instance.user_id = user_id
        instance.first_name = first_name
        instance.last_name = last_name
        instance.number_phone = number_phone
        instance.date_of_birth = date_of_birth
        instance.gender = gender.value
        instance.height = height
        instance.initial_weight = initial_weight
        instance.date_of_membership = date_of_membership
        instance.membership_status = membership_status.value
        instance.the_main_trainer = the_main_trainer
        instance.management_description = management_description
        instance.training_goal = training_goal
        instance.email = email
        instance.emergency_contact_number_if_needed = emergency_contact_number_if_needed
        return instance
    

    def update(self, first_name: str | None = None, last_name: str | None = None, number_phone: str | None = None,
               email: str | None = None, date_of_birth: date | None = None, gender: Gender | None = None,
               height: str | None = None, initial_weight: str | None = None, training_goal: str | None = None,
               date_of_membership: date | None = None, membership_status: MembershipStatusForAthlete | None = None,
               the_main_trainer: str | None = None, management_description: str | None = None, 
               emergency_contact_number_if_needed: str | None = None):
        
        self.first_name = first_name if first_name is not None else self.first_name
        self.last_name = last_name if last_name is not None else self.last_name
        self.number_phone = number_phone if number_phone is not None else self.number_phone
        self.email = email if email is not None else self.email
        self.date_of_birth = date_of_birth if date_of_birth is not None else self.date_of_birth
        self.height = height if height is not None else self.height
        self.initial_weight = initial_weight if initial_weight is not None else self.initial_weight
        self.training_goal = training_goal if training_goal is not None else self.training_goal
        self.date_of_membership = date_of_membership if date_of_membership is not None else self.date_of_membership
        self.the_main_trainer = the_main_trainer if the_main_trainer is not None else self.the_main_trainer
        self.management_description = management_description if management_description is not None else self.management_description
        self.emergency_contact_number_if_needed = emergency_contact_number_if_needed if emergency_contact_number_if_needed is not None else self.emergency_contact_number_if_needed
        if gender is not None:
            self.gender = gender
        if membership_status is not None:
            self.membership_status = membership_status


class AthleteSportsInfo(Base):
    __tablename__ = "athlete_sports_info"

    id = Column(Integer, primary_key=True, autoincrement=True)

    athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)

    main_goal = Column(Integer, nullable=False)             # هدف اصلی
    sport_level = Column(String(100), nullable=True)           # سطح ورزشی
    workout_experience = Column(String(255), nullable=True)    # سابقه تمرین
    weekly_sessions = Column(Integer, nullable=True)           # تعداد جلسات هفتگی
    injuries = Column(String(1000), nullable=True)             # آسیب‌دیدگی‌ها
    movement_limitations = Column(String(1000), nullable=True) # محدودیت‌های حرکتی
    food_allergies = Column(String(1000), nullable=True)       # حساسیت غذایی
    medical_explanations = Column(String(1500), nullable=True) # توضیحات پزشکی کاربر
    supplements_consumed = Column(String(1000), nullable=True) # مکمل‌های مصرفی
    coach_notes = Column(String(2000), nullable=True)          # یادداشت مربی

    # رابطه معکوس برای دسترسی راحت از این جدول به جدول پایه
    athlete = relationship("ProfileAthlete", back_populates="sports_info")


    @classmethod
    def create(cls, athlete_id: int, main_goal: MainGoal, sport_level: str | None = None, workout_experience: str | None = None,
               weekly_sessions: int | None = None, injuries: str | None = None, movement_limitations: str | None = None,
               food_allergies: str | None = None, medical_explanations: str | None = None, supplements_consumed: str | None = None,
               coach_notes: str | None = None):
        
        instance = cls()
        instance.athlete_id = athlete_id
        instance.main_goal = main_goal.value
        instance.sport_level = sport_level
        instance.workout_experience = workout_experience
        instance.weekly_sessions = weekly_sessions
        instance.injuries = injuries
        instance.movement_limitations = movement_limitations
        instance.food_allergies = food_allergies
        instance.medical_explanations = medical_explanations
        instance.supplements_consumed = supplements_consumed
        instance.coach_notes = coach_notes
        return instance
    

    def update(self, sport_level: str | None = None,
           workout_experience: str | None = None, weekly_sessions: int | None = None, 
           injuries: str | None = None, movement_limitations: str | None = None,
           food_allergies: str | None = None, medical_explanations: str | None = None, 
           supplements_consumed: str | None = None, coach_notes: str | None = None):
    
        self.sport_level = sport_level if sport_level is not None else self.sport_level
        self.workout_experience = workout_experience if workout_experience is not None else self.workout_experience
        self.weekly_sessions = weekly_sessions if weekly_sessions is not None else self.weekly_sessions
        self.injuries = injuries if injuries is not None else self.injuries
        self.movement_limitations = movement_limitations if movement_limitations is not None else self.movement_limitations
        self.food_allergies = food_allergies if food_allergies is not None else self.food_allergies
        self.medical_explanations = medical_explanations if medical_explanations is not None else self.medical_explanations
        self.supplements_consumed = supplements_consumed if supplements_consumed is not None else self.supplements_consumed
        self.coach_notes = coach_notes if coach_notes is not None else self.coach_notes
        
        
