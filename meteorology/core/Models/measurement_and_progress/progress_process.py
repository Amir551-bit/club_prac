from sqlalchemy import Column, String, Integer, func, Date, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import relationship
from sqlite.database import Base
from datetime import datetime, date
from core.execptions.execption import raise_bad_request


class ProgressProcess(Base):      # روند پیشرفت
    __tablename__="progress_process"
                                                                
    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)
    date_measurement = Column(Date, nullable=False)
    weight = Column(Integer, nullable=True)
    fat_percentage = Column(Float, nullable=True)
    around_neck = Column(Integer, nullable=True)   # دور گردن
    around_chest = Column(Integer, nullable=True)   # دور سینه
    around_arm = Column(Integer, nullable=True)      # دور بازو
    waist_circumference = Column(Integer, nullable=True)   # دور کمر
    abdominal_circumference = Column(Integer, nullable=True)   # دور شکم
    around_hips = Column(Integer, nullable=True)         # دور باسن
    around_thigh = Column(Integer, nullable=True)           # دور ران
    leg_circumference = Column(Integer, nullable=True)     # دور ساق
    description = Column(Text, nullable=True)
    data_recorder_coach = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)

    created_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    coach = relationship("ProfileCoach", back_populates="progress")
    athlete = relationship("ProfileAthlete", back_populates="progress")
    picture_progress = relationship("ProgressPicture", back_populates="progress")


    @classmethod
    def create(cls, athlete_id: int, date_measurement: date, data_recorder_coach: int, weight: int | None = None, fat_percentage: float | None = None,
                around_neck: int | None = None, around_chest: int | None = None, around_arm: int | None = None,
                waist_circumference: int | None = None, abdominal_circumference: int | None = None, around_thigh: int | None = None,
                leg_circumference: int | None = None, description: str | None = None):

        instance = cls()
        instance.athlete_id = athlete_id
        instance.date_measurement = date_measurement
        instance.weight = weight
        instance.fat_percentage = fat_percentage
        instance.around_neck = around_neck
        instance.around_chest = around_chest
        instance.around_arm = around_arm
        instance.waist_circumference = waist_circumference
        instance.abdominal_circumference = abdominal_circumference
        instance.around_thigh = around_thigh
        instance.leg_circumference = leg_circumference
        instance.description = description
        instance.data_recorder_coach = data_recorder_coach
        return instance



    def update(self, date_measurement: date | None = None, weight: int | None = None, fat_percentage: float | None = None, 
               around_neck: int | None = None, around_chest: int | None = None, around_arm: int | None = None, 
               waist_circumference: int | None = None, abdominal_circumference: int | None = None, around_thigh: int | None = None,
               leg_circumference: int | None = None, description: str | None = None):

        self.date_measurement = date_measurement if date_measurement is not None else self.date_measurement
        self.weight = weight if weight is not None else self.weight
        self.fat_percentage = fat_percentage if fat_percentage is not None else self.fat_percentage
        self.around_neck = around_neck if around_neck is not None else self.around_neck
        self.around_chest = around_chest if around_chest is not None else self.around_chest
        self.around_arm = around_arm if around_arm is not None else self.around_arm
        self.waist_circumference = waist_circumference if waist_circumference is not None else self.waist_circumference
        self.abdominal_circumference = abdominal_circumference if abdominal_circumference is not None else self.abdominal_circumference
        self.around_thigh = around_thigh if around_thigh is not None else self.around_thigh
        self.leg_circumference = leg_circumference if leg_circumference is not None else self.leg_circumference
        self.description = description if description is not None else self.description


class ProgressPicture(Base):
    __tablename__="progress_picture"

    id = Column(Integer, primary_key=True, autoincrement=True)
    progress_process_id = Column(Integer, ForeignKey("progress_process.id"), nullable=False)
    front_view = Column(String(200), nullable=True)
    side_view = Column(String(200), nullable=True)     # نمای کنار
    back_view = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    date_registration = Column(Date, default=func.current_date(),nullable=False)    
    data_recorder_coach = Column(Integer, ForeignKey("profile_coach.id"), nullable=True)    
    data_recorder_athlete = Column(Integer, ForeignKey("profile_athlete.id"), nullable=True)    

    created_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    athlete = relationship("ProfileAthlete", back_populates="picture_progress", foreign_keys=[data_recorder_athlete])
    coach = relationship("ProfileCoach", back_populates="picture_progress", foreign_keys=[data_recorder_coach])
    progress = relationship("ProgressProcess", back_populates="picture_progress")



    @classmethod
    def create_for_coach(cls, progress_process_id: int, data_recorder_coach: int, date_registration: date, front_view: str | None = None, 
                         side_view: str | None = None, back_view : str | None = None, description: str | None = None):

        instance = cls()
        instance.progress_process_id = progress_process_id
        instance.date_registration = date_registration
        instance.front_view = front_view
        instance.side_view = side_view
        instance.back_view = back_view
        instance.description = description
        instance.data_recorder_coach = data_recorder_coach
        return instance


    @classmethod
    def create_for_athlete(cls, progress_process_id: int, data_recorder_athlete: int, date_registration: date, front_view: str | None = None, 
                         side_view: str | None = None, back_view : str | None = None, description: str | None = None):

            instance = cls()
            instance.progress_process_id = progress_process_id
            instance.date_registration = date_registration
            instance.front_view = front_view
            instance.side_view = side_view
            instance.back_view = back_view
            instance.description = description
            instance.data_recorder_athlete = data_recorder_athlete
            return instance


    def update(self, date_registration: date | None = None, front_view: str | None = None, side_view: str | None = None,
               back_view : str | None = None, description: str | None = None):

        self.front_view = front_view if front_view is not None else self.front_view
        self.side_view = side_view if side_view is not None else self.side_view
        self.back_view = back_view if back_view is not None else self.back_view
        self.description = description if description is not None else self.description
        if date_registration is not None:
             self.date_registration = date_registration






