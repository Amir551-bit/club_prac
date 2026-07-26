from fastapi import Depends, APIRouter, Path, Query
from sqlalchemy.orm import Session
from core.Models.meal_plan.meal_plan import MealPlan, MealPlanDaily, FoodItems
from core.security.jwt_auth import get_current_user, check_admin
from controller.exercise_program_route.exercise_program_route import (accepted_coach_to_athlete, get_profile_athlete, get_profile_coach,
                                                                      get_profile_athlete_for_path)
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.profile.profile_coach_model import ProfileCoach
from sqlite.database import get_db
from core.Schemas.meal_plan.meal_plan_schemas import *
from core.Models.user.user_model import User
from core.Models.role.permission import Permission


meal_plan_router = APIRouter(prefix="/meal/plan", tags=["meal_plan"])



@meal_plan_router.post("/create/{profile_id}", response_model=MealPlanDailyResponse)
def create_meal_plan(request: CreateMealPlan,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
    new_meal_plan = MealPlan.create(athlete_profile.id, coach_profile.id, request.title, request.start_date, request.end_date, request)
    