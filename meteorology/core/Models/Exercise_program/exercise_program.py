from sqlalchemy import Column, String, Integer, func, Date, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlite.database import Base
from datetime import date
from core.Models.Exercise_program.exercise_program_enum import ProgramStatus, ActiveStatusMovement, DifficulityLevelMovement, ExeeciseIntencity



class ExerciseProgram(Base):
    __tablename__="exercise_program"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title_of_the_program = Column(String(200), nullable=False)
    athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)
    purpose_of_the_program = Column(String(200), nullable=False)
    start_date = Column(Date, default=func.now(), nullable=False)
    end_date = Column(Date, nullable=False)
    number_of_weekly_sessions = Column(Integer, nullable=False)
    general_description = Column(String(750), nullable=True)
    program_status = Column(Integer, nullable=False)
    program_version = Column(String(100), nullable=True)
    training_days = Column(String(500), nullable=False)
    coach_note = Column(String(300), nullable=True)

    created_date = Column(DateTime, server_default = func.now())
    update_date = Column(DateTime, server_default = func.now(), server_onupdate = func.now())


    coach = relationship("ProfileCoach", back_populates="program")
    athlete = relationship("ProfileAthlete", back_populates="program")
    daily_practices = relationship("DailyPractice", back_populates="exercise_program", cascade="all, delete-orphan")


    @classmethod
    def create(cls, title_of_the_program: str, athlete_id: int, coach_id: int, purpose_of_the_program: str, start_date: date, end_date: date, 
               number_of_weekly_sessions: int, program_status: ProgramStatus, training_days: str, general_description: str | None = None,
               program_version: str | None = None, coach_note: str | None = None):

        instance = cls()
        instance.title_of_the_program = title_of_the_program
        instance.athlete_id = athlete_id
        instance.coach_id = coach_id
        instance.purpose_of_the_program = purpose_of_the_program
        instance.start_date = start_date
        instance.end_date = end_date
        instance.number_of_weekly_sessions = number_of_weekly_sessions
        instance.general_description = general_description
        instance.program_status = program_status.value
        instance.program_version = program_version
        instance.training_days = training_days
        instance.coach_note = coach_note
        return instance


    def update(self, title_of_the_program: str | None = None, purpose_of_the_program: str | None = None, start_date: date | None = None, 
               end_date: date | None = None, number_of_weekly_sessions: int | None = None, program_status: ProgramStatus | None = None, 
               training_days: str | None = None, general_description: str | None = None, program_version: str | None = None, coach_note: str | None = None) :

        self.title_of_the_program = title_of_the_program if title_of_the_program is not None else self.title_of_the_program
        self.purpose_of_the_program = purpose_of_the_program if purpose_of_the_program is not None else self.purpose_of_the_program
        self.start_date = start_date if start_date is not None else self.start_date
        self.end_date = end_date if end_date is not None else self.end_date
        self.number_of_weekly_sessions = number_of_weekly_sessions if number_of_weekly_sessions is not None else self.number_of_weekly_sessions
        self.general_description = general_description if general_description is not None else self.general_description
        self.program_status = program_status.value if program_status is not None else self.program_status
        self.program_version = program_version if program_version is not None else self.program_version
        self.training_days = training_days if training_days is not None else self.training_days
        self.coach_note = coach_note if coach_note is not None else self.coach_note


class DailyPractice(Base):
    __tablename__="daily_practice"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_program_id = Column(Integer, ForeignKey("exercise_program.id"), nullable=False)
    title_session = Column(String(200), nullable=False)
    day_number = Column(Integer, nullable=False)
    description = Column(String(750), nullable=False)
    warm_up = Column(Boolean, default=True)
    cardio = Column(String(500), nullable=True)   #  تمرین هوازی
    cool_down = Column(String(500), nullable=True)


    created_date = Column(DateTime, server_default = func.now())
    update_date = Column(DateTime, server_default = func.now(), server_onupdate = func.now())

    exercise_program = relationship("ExerciseProgram", back_populates="daily_practices")
    movements_info = relationship("InformationForMovement", back_populates="daily_practice", cascade="all, delete-orphan")


    @classmethod
    def create(cls, exercise_program_id: int, title_session: str, day_number: int, description: str, warm_up: bool,
            cardio: str| None = None, cool_down: str | None = None):

        instance = cls()
        instance.exercise_program_id = exercise_program_id
        instance.title_session = title_session
        instance.day_number = day_number
        instance.description = description
        instance.warm_up = warm_up
        instance.cardio = cardio
        instance.cool_down = cool_down
        return instance


    def update(self, title_session: str | None = None, day_number: int | None = None, description: str | None = None,
                warm_up: bool | None = None, cardio: str| None = None, cool_down: str | None = None):

        self.title_session = title_session if title_session is not None else self.title_session
        self.day_number = day_number if day_number is not None else self.day_number
        self.description = description if description is not None else self.description
        self.warm_up = warm_up if warm_up is not None else self.warm_up
        self.cardio = cardio if cardio is not None else self.cardio
        self.cool_down = cool_down if cool_down is not None else self.cool_down



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

    created_date = Column(DateTime, server_default = func.now())
    update_date = Column(DateTime, server_default = func.now(), server_onupdate = func.now())

    info_for_move = relationship("InformationForMovement", back_populates="move_bank")



    @classmethod
    def create(cls, persion_name: str, english_name: str, category: str , target_muscle: str, auxiliary_muscles: str, required_equipment: str,        
               difficulty_level: DifficulityLevelMovement, description_for_move: str, executive_warnings: str, active_status: ActiveStatusMovement,
               image: str | None = None, video_link: str| None = None):

        instance = cls()
        instance.persion_name = persion_name
        instance.english_name = english_name
        instance.category = category
        instance.target_muscle = target_muscle
        instance.auxiliary_muscles = auxiliary_muscles
        instance.required_equipment = required_equipment
        instance.difficulty_level = difficulty_level.value
        instance.description_for_move = description_for_move
        instance.executive_warnings = executive_warnings
        instance.active_status = active_status.value
        instance.image = image 
        instance.video_link = video_link
        return instance


    def update(self, persion_name: str | None = None, english_name: str | None = None, category: str | None = None, target_muscle: str | None = None, 
               auxiliary_muscles: str | None = None, required_equipment: str | None = None, difficulty_level: DifficulityLevelMovement | None = None, 
               description_for_move: str | None = None, executive_warnings: str | None = None, active_status: ActiveStatusMovement | None = None,
               image: str | None = None, video_link: str| None = None):

        self.persion_name = persion_name if persion_name is not None else self.persion_name
        self.english_name = english_name if english_name is not None else self.english_name
        self.category = category if category is not None else self.category
        self.target_muscle = target_muscle if target_muscle is not None else self.target_muscle
        self.auxiliary_muscles = auxiliary_muscles if auxiliary_muscles is not None else self.auxiliary_muscles
        self.required_equipment = required_equipment if required_equipment is not None else self.required_equipment
        self.difficulty_level = difficulty_level.value if difficulty_level is not None else self.difficulty_level
        self.description_for_move = description_for_move if description_for_move is not None else self.description_for_move
        self.executive_warnings = executive_warnings if executive_warnings is not None else self.executive_warnings
        self.active_status = active_status.value if active_status is not None else self.active_status
        self.image = image if image is not None else self.image
        self.video_link = video_link if video_link is not None else self.video_link



class InformationForMovement(Base):
    __tablename__="information_for_movement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movement_bank_id = Column(Integer, ForeignKey("movement_bank.id"), nullable=False)
    daily_practice_id = Column(Integer, ForeignKey("daily_practice.id"), nullable=False)
    move_name = Column(String(150), nullable=False)
    move_picture = Column(String(200), nullable=True)
    link_video = Column(String(200), nullable=True)
    set_number = Column(Integer, nullable=False)
    number_of_repeat = Column(Integer, nullable=False)
    suggested_weight = Column(Integer, nullable=True)
    practice_time = Column(String(50), nullable=False)
    rest_time = Column(String(50), nullable=False)
    tempo = Column(String(100), nullable=False)
    exercise_intensity = Column(Integer, nullable=False)        # شدت تمرین
    description_coach = Column(String(750), nullable=True)
    display_order = Column(Integer, nullable=False)   # ترتیب نمایش
    alternate_move = Column(String(300), nullable=True)     # حرکت جایگزین 
    being_a_superset_or_a_dropset = Column(Boolean, default=False)  


    created_date = Column(DateTime, server_default = func.now())
    update_date = Column(DateTime, server_default = func.now(), server_onupdate = func.now())

    move_bank = relationship("MovementBank", back_populates="info_for_move")
    daily_practice = relationship("DailyPractice", back_populates="movements_info")
    registrations = relationship("RegistrationDailyPractice", back_populates="movements_info")


    @classmethod
    def create(cls, movement_bank_id: int, daily_practice_id: int, move_name: str, set_number: int, number_of_repeat: int, practice_time: str,rest_time: str,
               tempo: str, exercise_intensity: ExeeciseIntencity, display_order: int, being_a_superset_or_a_dropset: bool, move_picture: str | None = None,
               link_video: str | None = None, suggested_weight: int | None = None, description_coach: str | None = None, alternate_move: str | None = None):

        instance = cls()
        instance.movement_bank_id = movement_bank_id
        instance.daily_practice_id = daily_practice_id
        instance.move_name = move_name
        instance.move_picture = move_picture
        instance.link_video = link_video
        instance.set_number = set_number
        instance.number_of_repeat = number_of_repeat
        instance.suggested_weight = suggested_weight
        instance.practice_time = practice_time
        instance.rest_time = rest_time
        instance.tempo = tempo
        instance.exercise_intensity = exercise_intensity.value
        instance.description_coach = description_coach
        instance.display_order = display_order
        instance.alternate_move = alternate_move
        instance.being_a_superset_or_a_dropset = being_a_superset_or_a_dropset
        return instance


    def update(self, move_name: str | None = None, move_picture: str | None = None, link_video: str | None = None, set_number: int | None = None,
        number_of_repeat: int | None = None, suggested_weight: int | None = None, practice_time: str | None = None, rest_time: str | None = None,
        tempo: str | None = None, exercise_intensity: ExeeciseIntencity | None = None, description_coach: str | None = None, display_order: int | None = None,
        alternate_move: str | None = None, being_a_superset_or_a_dropset: bool | None = None):


        self.move_name = move_name if move_name is not None else self.move_name
        self.move_picture = move_picture if move_picture is not None else self.move_picture
        self.link_video = link_video if link_video is not None else self.link_video
        self.set_number = set_number if set_number is not None else self.set_number
        self.number_of_repeat = number_of_repeat if number_of_repeat is not None else self.number_of_repeat
        self.suggested_weight = suggested_weight if suggested_weight is not None else self.suggested_weight
        self.practice_time = practice_time if practice_time is not None else self.practice_time
        self.rest_time = rest_time if rest_time is not None else self.rest_time
        self.tempo = tempo if tempo is not None else self.tempo
        self.exercise_intensity = exercise_intensity.value if exercise_intensity is not None else self.exercise_intensity
        self.description_coach = description_coach if description_coach is not None else self.description_coach
        self.display_order = display_order if display_order is not None else self.display_order
        self.alternate_move = alternate_move if alternate_move is not None else self.alternate_move
        self.being_a_superset_or_a_dropset = being_a_superset_or_a_dropset if being_a_superset_or_a_dropset is not None else self.being_a_superset_or_a_dropset




class RegistrationDailyPractice(Base):
    __tablename__="registration_practice"

    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)
    information_for_movement_id = Column(Integer, ForeignKey("information_for_movement.id"), nullable=False)
    done_status = Column(Boolean, default=False, nullable=False)
    done_date = Column(Date, default=func.current_date(), nullable=False)
    actual_weight_used = Column(Integer, nullable=True)
    actual_number_repeat = Column(Integer, nullable=False)
    difficulty_exercise = Column(Integer, nullable=False)
    time_practice = Column(Integer, nullable=False)
    description_for_coach = Column(Text, nullable=True)
    Problem_during_exercise = Column(Text, nullable=True)

    created_date = Column(DateTime, server_default = func.now())
    update_date = Column(DateTime, server_default = func.now(), server_onupdate = func.now())

    athlete = relationship("ProfileAthlete", back_populates="regis_daily_practice")
    movements_info = relationship("InformationForMovement", back_populates="registrations")




