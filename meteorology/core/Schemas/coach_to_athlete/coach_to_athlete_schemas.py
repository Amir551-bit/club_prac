from pydantic import BaseModel, ConfigDict
from core.Models.connection_coach_to_athlete.coach_to_athlete_enum import CoachTypeEnum, ConnectionStatusEnum
from datetime import date



class CreateCoachToAthlete(BaseModel):
    profile_coach_id: int
    profile_athlete_id: int 
    start_date: date
    status: ConnectionStatusEnum
    coach_role: CoachTypeEnum
    manager_notes: str | None = None 
    end_date: date | None = None



class UpdateCoachToAthlete(BaseModel):
    start_date: date | None = None
    status: ConnectionStatusEnum | None = None
    coach_role: CoachTypeEnum | None = None
    manager_notes: str | None = None 
    end_date: date | None = None



class CoachToAthleteResponse(BaseModel):
    profile_coach_id: int
    profile_athlete_id: int 
    start_date: date
    status: ConnectionStatusEnum
    coach_role: CoachTypeEnum
    manager_notes: str | None = None 
    end_date: date | None = None

    model_config = ConfigDict(from_attributes=True)



class CoachToAthleteResponses(BaseModel):
    items: list[CoachToAthleteResponse]
    total: int
    limit: int
    offset: int



