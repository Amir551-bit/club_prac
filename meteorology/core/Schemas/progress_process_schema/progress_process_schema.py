from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from core.Schemas.profile.profile_athlete import ProfileAthleteResponse
from core.Schemas.profile.profile_coach import ProfileCoachResponse


class CreateProgressProcess(BaseModel):
    date_measurement: date
    weight: int | None = None
    fat_percentage: float | None = None
    around_neck: int | None = None 
    around_chest: int | None = None 
    around_arm: int | None = None
    waist_circumference: int | None = None 
    abdominal_circumference: int | None = None 
    around_thigh: int | None = None
    leg_circumference: int | None = None
    description: str | None = None



class UpdateProgressProcess(BaseModel):
    date_measurement: date | None = None
    weight: int | None = None
    fat_percentage: float | None = None
    around_neck: int | None = None 
    around_chest: int | None = None 
    around_arm: int | None = None
    waist_circumference: int | None = None 
    abdominal_circumference: int | None = None 
    around_thigh: int | None = None
    leg_circumference: int | None = None
    description: str | None = None



class ProgressProcessResponse(BaseModel):
    athlete_id: int
    date_measurement: date
    data_recorder_coach: int
    weight: int | None = None
    fat_percentage: float | None = None
    around_neck: int | None = None 
    around_chest: int | None = None 
    around_arm: int | None = None
    waist_circumference: int | None = None 
    abdominal_circumference: int | None = None 
    around_thigh: int | None = None
    leg_circumference: int | None = None
    description: str | None = None
    created_date: datetime
    update_date: datetime

    model_config = ConfigDict(from_attributes=True)


class ProgressProcessResponseForOne(ProgressProcessResponse):

    athlete_profile: ProfileAthleteResponse


class ProgressProcessResponses(BaseModel):
     items : list[ProgressProcessResponse]
     total : int
     limit : int
     offset : int
     profile_athlete : ProfileAthleteResponse
     profile_coach : ProfileCoachResponse


class CreateProgressPicture(BaseModel):
    date_registration: date 
    front_view: str | None = None 
    side_view: str | None = None
    back_view : str | None = None 
    description: str | None = None



class UpdateProgressPicture(BaseModel):
    date_registration: date | None = None
    front_view: str | None = None 
    side_view: str | None = None
    back_view : str | None = None 
    description: str | None = None



class ProgressPictureResponse(BaseModel):
       progress_process_id: int
       date_registration: date 
       front_view: str | None = None 
       side_view: str | None = None
       back_view : str | None = None 
       description: str | None = None
       data_recorder_coach: int | None = None
       data_recorder_athlete: int | None = None

       model_config = ConfigDict(from_attributes=True)


class ProgressPictureResponseOne(ProgressPictureResponse):
     progress_process: ProgressProcessResponse




