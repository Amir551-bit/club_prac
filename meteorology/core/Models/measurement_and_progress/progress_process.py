from sqlalchemy import Column, String, Integer, func, Date, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlite.database import Base



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


    coach = relationship("ProfileCoach", back_populates="progress")
    athlete = relationship("ProfileAthlete", back_populates="progress")



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


    athlete = relationship("ProfileAthlete", back_populates="picture_progress", foreign_keys=[data_recorder_athlete])
    coach = relationship("ProfileCoach", back_populates="picture_progress", foreign_keys=[data_recorder_coach])







