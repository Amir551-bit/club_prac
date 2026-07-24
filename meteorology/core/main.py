from fastapi import FastAPI, Depends
from sqlite.database import Base, get_db, Sessionlocal
from sqlite.database import engine
from contextlib import asynccontextmanager
from core.security.jwt_auth import get_current_user, security
from core.db_helper.db_helper import seeds_role, create_admin

from core.Models.club.club_model import Club
from core.Models.connection_coach_to_athlete.coach_to_athlete import CoachAthleteConnection
from core.Models.Exercise_program.exercise_program import (ExerciseProgram, DailyPractice, MovementBank, 
InformationForMovement, RegistrationDailyPractice)
from core.Models.meal_plan.meal_plan import MealPlan, MealPlanDaily, FoodItems
from core.Models.measurement_and_progress.progress_process import ProgressPicture, ProgressProcess
from core.Models.profile.profile_athlete_model import ProfileAthlete, AthleteSportsInfo
from core.Models.profile.profile_coach_model import ProfileCoach, Specialties
from core.Models.role.role_model import Role
from core.Models.user_role.user_role_model import UserRole
from core.Models.user.user_model import User

from controller.user.user_route import user_route
from controller.profile_coach.profile_coach_route import profile_coach_router
from controller.profile_athlete.profile_athlete_route import profile_athlete_route
from controller.profile_athlete.profile_athlete_route import athlete_sport_info
from controller.profile_coach.profile_coach_route import specialties_coach_router
from controller.club.club_route import club_router
from controller.club.club_route import club_amenity_router
from controller.club.club_route import club_gallery_router
from controller.coach_to_athlete.coach_to_athlete_route import coach_to_athlete_router
from controller.exercise_program_route.exercise_program_route import exercise_program_router
from controller.user_role.user_role_route import user_role_router

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting server ...")
    try:
        seeds_role()
        create_admin()
    except Exception as e:
        print(f"❌ Error while seeding roles: {e}")
    yield
    print("Server is shutting down...")

# 🟢 ۲. اضافه کردن دپندسی سراسری برای فعال شدن دکمه Authorize در بالای Swagger
app = FastAPI(lifespan=lifespan)

app.include_router(user_route)
app.include_router(profile_coach_router)
app.include_router(profile_athlete_route)
app.include_router(athlete_sport_info)
app.include_router(specialties_coach_router)
app.include_router(club_router)
app.include_router(club_amenity_router)
app.include_router(club_gallery_router)
app.include_router(coach_to_athlete_router)
app.include_router(exercise_program_router)
app.include_router(user_role_router)



@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/profile")
def read_user_profile(current_user = Depends(get_current_user)):
    return {"message": "خوش آمدید", "user": current_user.user_name}