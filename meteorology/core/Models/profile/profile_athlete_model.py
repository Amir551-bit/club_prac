from sqlalchemy import Column, String, Integer, func, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlite.database import Base
from core.Models.profile.profile_enum import MembershipStatusForAthlete



class ProfileAthlete(Base):
    __tablename__="profile_athlete"

    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    number_phone = Column(String(11), nullable=False, unique=True)
    email = Column(String(150), nullable=True, unique=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    initial_weight = Column(Integer, nullable=False)
    training_goal = Column(String(1000), nullable=True)
    Date_of_membership = Column(Date, nullable=False)
    Membership_status = Column(Integer, default=MembershipStatusForAthlete.yes.value, nullable=False)
    The_main_trainer = Column(String(150), nullable=False)
    Management_description = Column(String(1500), nullable=True)
    Emergency_contact_number_if_needed = Column(String(11), nullable=True)


    sports_info = relationship("AthleteSportsInfo", back_populates="athlete", uselist=False)
    coach_to_athlete = relationship("CoachAthleteConnection", back_populates="athlete")
    program = relationship("ProfileAthlete", back_populates="athlete")


class AthleteSportsInfo(Base):
    __tablename__ = "athlete_sports_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # اتصال به جدول اصلی از طریق کلید خارجی
    athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), unique=True, nullable=False)

    main_goal = Column(Integer, nullable=True)             # هدف اصلی
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