from pydantic import BaseModel, ConfigDict
from core.Models.Exercise_program.exercise_program_enum import (ProgramStatus, DifficulityLevelMovement, 
                                                                ActiveStatusMovement, Time, ExeeciseIntencity)
from datetime import date, datetime
from core.Models.notification_system.notification_system_enum import NotificationsRequiredEnum

class CreateExerciseProgram(BaseModel):

        title_of_the_program: str
        purpose_of_the_program: str
        start_date: date
        end_date: date 
        number_of_weekly_sessions: int
        general_description: str | None = None 
        program_status: ProgramStatus
        program_version: str | None = None
        training_days: str 
        coach_note: str | None = None 


class UpdateExerciseProgram(BaseModel):
        
        title_of_the_program: str | None = None
        purpose_of_the_program: str | None = None
        start_date: date | None = None
        end_date: date | None = None
        number_of_weekly_sessions: int | None = None
        general_description: str | None = None  
        program_status: ProgramStatus | None = None
        program_version: str | None = None
        training_days: str | None = None
        coach_note: str | None = None 


class ExerciseProgramResponse(BaseModel):
        title_of_the_program: str
        athlete_id: int
        coach_id: int
        purpose_of_the_program: str
        start_date: date
        end_date: date 
        number_of_weekly_sessions: int
        general_description: str | None = None 
        program_status: ProgramStatus
        program_version: str | None = None
        training_days: str 
        coach_note: str | None = None
        created_date: datetime
        update_date: datetime

        model_config = ConfigDict(from_attributes=True)


class ExerciseProgramResponses(BaseModel):
        items: list[ExerciseProgramResponse]
        total: int
        limit: int
        offset: int


# program daily

class CreateProgramDaily(BaseModel):
        title_session: str
        day_number: int
        description: str 
        warm_up: bool
        cardio: str| None = None    
        cool_down: str | None = None


class UpdateProgramDaily(BaseModel):
        title_session: str | None = None
        day_number: int | None = None
        description: str | None = None
        warm_up: bool | None = None
        cardio: str| None = None    
        cool_down: str | None = None



class ProgramDailyResponse(BaseModel):
        exercise_program_id: int
        title_session: str
        day_number: int
        description: str 
        warm_up: bool
        cardio: str| None = None    
        cool_down: str | None = None
        created_date: datetime
        update_date: datetime

        model_config = ConfigDict(from_attributes=True)


class ProgramDailyResponseForOne(BaseModel):
        daily_practice: ProgramDailyResponse
        exercise_program: ExerciseProgramResponse

        model_config = ConfigDict(from_attributes=True)


class ProgramDailyResponses(BaseModel):
        items: list[ProgramDailyResponse]
        total: int
        program: ExerciseProgramResponse


# MovementBunk


class CreateMovementBank(BaseModel):

        persion_name: str
        english_name: str
        category: str 
        target_muscle: str 
        auxiliary_muscles: str
        required_equipment: str            
        difficulty_level: DifficulityLevelMovement
        description_for_move: str
        executive_warnings: str   
        active_status: ActiveStatusMovement
        image: str | None = None
        video_link: str | None = None



class UpdateMovementBank(BaseModel):

        persion_name: str | None = None
        english_name: str | None = None
        category: str | None = None
        target_muscle: str | None = None
        auxiliary_muscles: str | None = None
        required_equipment: str | None = None         
        difficulty_level: DifficulityLevelMovement | None = None
        description_for_move: str | None = None
        executive_warnings: str | None = None
        image: str | None = None
        video_link: str | None = None
        active_status: ActiveStatusMovement | None = None



class MovementBankresponse(BaseModel):

        persion_name: str
        english_name: str
        category: str 
        target_muscle: str 
        auxiliary_muscles: str
        required_equipment: str            
        difficulty_level: DifficulityLevelMovement
        description_for_move: str
        executive_warnings: str   
        active_status: ActiveStatusMovement
        image: str | None = None
        video_link: str | None = None
        created_date: datetime
        update_date: datetime

        model_config = ConfigDict(from_attributes=True)


class MovementBankresponses(BaseModel):
        items: list[MovementBankresponse]
        total: int
        limit: int
        offset: int


# Information Movement


class CreateInformationForMovement(BaseModel):

        move_name: str
        move_picture: str | None = None
        link_video: str | None = None
        set_number: int
        number_of_repeat: int
        suggested_weight: int | None = None
        practice_time: str
        rest_time: str
        tempo: str
        exercise_intensity: ExeeciseIntencity
        description_coach: str | None = None
        display_order: int
        alternate_move: str | None = None
        being_a_superset_or_a_dropset: bool



class UpdateInformationForMovement(BaseModel):

        move_name: str | None = None
        move_picture: str | None = None
        link_video: str | None = None
        set_number: int | None = None
        number_of_repeat: int | None = None
        suggested_weight: int | None = None
        practice_time: str | None = None
        rest_time: str | None = None
        tempo: str | None = None
        exercise_intensity: ExeeciseIntencity | None = None
        description_coach: str | None = None 
        display_order: int | None = None
        alternate_move: str | None = None
        being_a_superset_or_a_dropset: bool | None = None


class InformationForMovementResponse(BaseModel):

        move_name: str
        move_picture: str | None = None
        link_video: str | None = None
        set_number: int
        number_of_repeat: int
        suggested_weight: int | None = None
        practice_time: str
        rest_time: str
        tempo: str
        exercise_intensity: ExeeciseIntencity
        description_coach: str | None = None
        display_order: int
        alternate_move: str | None = None
        being_a_superset_or_a_dropset: bool


        model_config = ConfigDict(from_attributes=True)


class InformationForMovementResponses(BaseModel):
        items: list[InformationForMovementResponse]
        total: int
        limit: int
        offset: int
        daily_practice: ProgramDailyResponse



# Registration_Daily_Practice


class CreateRegistrationDailyPractice(BaseModel):

        done_status: bool
        done_date: date
        actual_weight_used: int
        actual_number_repeat: int
        difficulty_exercise: ExeeciseIntencity
        time_practice: str
        description_for_coach: str | None = None
        problem_during_exercise: str | None = None




class UpdateRegistrationDailyPractice(BaseModel):

        done_status: bool | None = None
        done_date: date | None = None
        actual_weight_used: int | None = None
        actual_number_repeat: int | None = None
        difficulty_exercise: ExeeciseIntencity | None = None
        time_practice: str | None = None
        description_for_coach: str | None = None
        problem_during_exercise: str | None = None



class RegistrationDailyPracticeResponse(BaseModel):

        done_status: bool
        done_date: date
        actual_weight_used: int
        actual_number_repeat: int
        difficulty_exercise: ExeeciseIntencity
        time_practice: str
        description_for_coach: str | None = None
        problem_during_exercise: str| None = None


        model_config = ConfigDict(from_attributes=True)




class CreateNotification(BaseModel):
    
    title: str
    text: str
    type: NotificationsRequiredEnum
    read_status: bool = False

