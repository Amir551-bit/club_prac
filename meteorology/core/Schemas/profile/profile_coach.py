from pydantic import BaseModel, ConfigDict, field_validator
from core.Models.profile.profile_enum import (Gender, MembershipStatusForAthlete, MainGoal,
                                              SpecialtiesEnum, CooperationStatusForCoach)
from datetime import date



class CreateProfileCoach(BaseModel):
    first_name: str
    last_name: str
    number_phone: str
    email: str | None = None
    bio: str | None = None
    work_history: str
    documents_and_certificates: str
    area_of_activity: str
    social_networks: str | None = None
    attendance_hours: str
    cooperation_status: CooperationStatusForCoach


class UpdateProfileCoach(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    number_phone: str | None = None
    email: str | None = None
    bio: str | None = None
    work_history: str | None = None
    documents_and_certificates: str | None = None
    area_of_activity: str | None = None
    social_networks: str | None = None
    attendance_hours: str | None = None
    cooperation_status: CooperationStatusForCoach | None = None



class ProfileCoachResponse(BaseModel):
    first_name: str
    last_name: str
    number_phone: str
    email: str | None = None
    bio: str | None = None
    work_history: str
    documents_and_certificates: str
    area_of_activity: str
    social_networks: str | None = None
    attendance_hours: str
    cooperation_status: CooperationStatusForCoach

    model_config = ConfigDict(from_attributes=True)


class ChangeStatusCoach(BaseModel):
    status: CooperationStatusForCoach



class ProfileCoachResponses(BaseModel):
    items : list[ProfileCoachResponse]
    total: int
    limit: int
    offset: int


# Specialties

class CreateCoachSpecialties(BaseModel):
    specialties: SpecialtiesEnum


class UpdateCoachSpecialties(BaseModel):
    specialties: SpecialtiesEnum | None = None



class SpecialtiesResponse(BaseModel):
    profile_id: int
    specialties: SpecialtiesEnum

    model_config = ConfigDict(from_attributes=True)


class SpecialtiesResponses(BaseModel):
    items: list[SpecialtiesResponse]
    total: int
    limit: int
    offset: int


class SpecialtiesResponsesWithProfile(BaseModel):
    profile: ProfileCoachResponse
    items: list[SpecialtiesResponse]
    total: int
    limit: int
    offset: int





