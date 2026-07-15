from sqlalchemy import Column, String, Integer, func, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlite.database import Base



class ExerciseProgram(Base):
    __tablename__="exercise_program"

    id = Column(Integer, primary_key=True, autoincrement=True)
    Title_of_the_program = Column(String(200), nullable=False)
    athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)
    Purpose_of_the_program = Column(String(200), nullable=False)
    start_date = Column(Date, default=func.now(), nullable=False)
    end_date = Column(Date, nullable=False)
    number_of_weekly_sessions = Column(Integer, nullable=False)
    general_description = Column(String(750), nullable=True)
    program_status = Column(Integer, nullable=False)
    program_version = Column(String(100), nullable=True)
    training_days = Column(String(500), nullable=False)
    coach_note = Column(String(300), nullable=True)


    coach = relationship("ProfileCoach", back_populates="program")
    athlete = relationship("ProfileAthlete", back_populates="program")




class DailyPractice(Base):
    __tablename__="daily_practice"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_program_id = Column(Integer, ForeignKey("exercise_program.id"), nullable=False)
    title_session = Column(String(200), nullable=False)
    day_number = Column(Integer, nullable=False)
    description = Column(String(750), nullable=False)




class MovementBank(Base):
    __tablename__="movement_bank"

    id = Column(Integer, primary_key=True, autoincrement=True)
    persion_name = Column(String(200), nullable=False)
    english_name = Column(String(200), nullable=False)
    category = Column(String(200), nullable=False)
    target_muscle = Column(String(200), nullable=False)
    auxiliary_muscles = Column(String(200), nullable=False)
    required_equipment = Column(String(500), nullable=False)                      # تجهیزات مورد نیاز
    difficulty_level = Column(Integer, nullable=False)
    description_for_move = Column(String(5000), nullable=False)
    executive_warnings = Column(String(1000), nullable=False)           # هشدار های اجرایی
    image = Column(String(200), nullable=True)
    video_link = Column(String(200), nullable=True)
    active_status = Column(Integer, nullable=False)



class InformationForMovement(Base):
    



