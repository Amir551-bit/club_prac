from pydantic import BaseModel, ConfigDict, field_validator
from core.Models.profile.profile_enum import (Gender, MembershipStatusForAthlete, MainGoal,
                                              SpecialtiesEnum, CooperationStatusForCoach)
from datetime import date, datetime
from core.Models.notification_system.notification_system_enum import NotificationsRequiredEnum


class CreateProfileAthleteSchema(BaseModel):
    user_id: int
    first_name: str 
    last_name: str 
    number_phone: str 
    email: str | None = None 
    date_of_birth: date
    gender: Gender 
    height: str
    initial_weight: str
    training_goal: str | None = None
    date_of_membership:  date
    membership_status: MembershipStatusForAthlete
    the_main_trainer: str 
    management_description: str | None = None 
    emergency_contact_number_if_needed: str | None = None 

    
    @field_validator("height", mode="plain")
    def validator_height(cls, value) -> str:
        value_str = str(value).strip()
        if not value_str.endswith("cm"):
            return f"{value_str}cm"
        return value_str
    
    @field_validator("initial_weight", mode="plain")
    def validator_weight(cls, value) -> str:
        value_str = str(value).strip()
        if not value_str.endswith("kg"):
            return f"{value_str}kg"
        return value_str
    

class ProfileAthleteResponse(BaseModel):
    first_name: str 
    last_name: str 
    number_phone: str 
    email: str | None = None 
    date_of_birth: date
    gender: Gender 
    height: str
    initial_weight: str
    training_goal: str | None = None
    date_of_membership:  date
    membership_status: MembershipStatusForAthlete
    the_main_trainer: str 
    management_description: str | None = None 
    emergency_contact_number_if_needed: str | None = None 
    created_date: datetime
    update_date: datetime

    model_config = ConfigDict(from_attributes=True)



class UpdateProfileAthlete(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    number_phone: str | None = None
    email: str | None = None 
    date_of_birth: date | None = None
    gender: Gender | None = None
    height: str | None = None
    initial_weight: str | None = None
    training_goal: str | None = None
    date_of_membership:  date | None = None
    the_main_trainer: str | None = None
    management_description: str | None = None 
    emergency_contact_number_if_needed: str | None = None 

    # @field_validator("height", mode="before")
    # def validator_height(cls, value) -> str:
    #     if value is not None:
    #         value_str = str(value).strip()
    #         if not value_str.endswith("cm"):
    #             return f"{value_str}cm"
    #         return value_str
    
    # @field_validator("initial_weight", mode="before")
    # def validator_weight(cls, value) -> str:
    #     if value is not None:
    #         value_str = str(value).strip()
    #         if not value_str.endswith("kg"):
    #             return f"{value_str}kg"
    #         return value_str



class ChangeStatusMembership(BaseModel):
    status: MembershipStatusForAthlete


class CreateNotification(BaseModel):
    
    title: str
    text: str
    type: NotificationsRequiredEnum
    read_status: bool = False




class ProfileAthleteResponses(BaseModel):
    items: list[ProfileAthleteResponse]
    total: int
    limit: int
    offset: int




class CreateAthleteSportsInfo(BaseModel):

    athlete_id: int
    main_goal: MainGoal 
    sport_level: str | None = None 
    workout_experience: str | None = None 
    weekly_sessions: int | None = None 
    injuries: str | None = None
    movement_limitations: str | None = None 
    food_allergies: str | None = None 
    medical_explanations: str | None = None 
    supplements_consumed: str | None = None 
    coach_notes: str | None = None


class UpdateAthleteSportsInfo(BaseModel):
    
    sport_level: str | None = None 
    workout_experience: str | None = None 
    weekly_sessions: int | None = None 
    injuries: str | None = None
    movement_limitations: str | None = None 
    food_allergies: str | None = None 
    medical_explanations: str | None = None 
    supplements_consumed: str | None = None 
    coach_notes: str | None = None



class AthleteSportsInfoResponse(BaseModel):

    athlete_id: int
    main_goal: MainGoal 
    sport_level: str | None = None 
    workout_experience: str | None = None 
    weekly_sessions: int | None = None 
    injuries: str | None = None
    movement_limitations: str | None = None 
    food_allergies: str | None = None 
    medical_explanations: str | None = None 
    supplements_consumed: str | None = None 
    coach_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)



class AthleteSportsInfoResponses(BaseModel):
    items: list[AthleteSportsInfoResponse]
    total: int
    limit: int
    offset: int


