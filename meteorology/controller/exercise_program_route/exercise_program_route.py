from fastapi import APIRouter, Depends, Path, Query
from core.Models.user.user_model import User
from core.Models.Exercise_program.exercise_program import ExerciseProgram, DailyPractice, MovementBank, InformationForMovement, RegistrationDailyPractice
from core.Schemas.exercise_program_schemas.exercise_program_schemas import *
from core.security.jwt_auth import get_current_user, check_admin
from sqlite.database import get_db
from sqlalchemy.orm import Session
from core.Models.role.permission import Permission
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from core.Models.connection_coach_to_athlete.coach_to_athlete import CoachAthleteConnection
from core.Models.profile.profile_coach_model import ProfileCoach
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.connection_coach_to_athlete.coach_to_athlete_enum import ConnectionStatusEnum


exercise_program_router = APIRouter(prefix="/exercise/program", tags=["exercise_program"])


def get_profile_coach(user_id: int, db: Session):
    exists = db.query(ProfileCoach).filter(ProfileCoach.user_id==user_id).first()
    if not exists:
        raise_not_found("profile coach is not found")
    return exists

def get_profile_athlete_for_path(profile_id: int = Path(...), 
                        db: Session = Depends(get_db)):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.id==profile_id).first()
    if not exists:
        raise_not_found("profile athlete is not found")
    return exists

def get_profile_athlete(profile_id: int, db: Session):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.id==profile_id).first()
    if not exists:
        raise_not_found("profile athlete is not found")
    return exists


def get_profile_athlete_with_user_id(user_id: int,
                                     db: Session):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.user_id==user_id).first()
    if not exists:
        raise_not_found("profile is not found")
    return exists

def accepted_coach_to_athlete(coach_id: int, athlete_id: int, db: Session):
    accepted = db.query(CoachAthleteConnection).filter(CoachAthleteConnection.profile_coach_id==coach_id,
                                                           CoachAthleteConnection.profile_athlete_id==athlete_id,
                                                           CoachAthleteConnection.status==1).first()
    if not accepted:
        raise_bad_request("you have not coach this athlete")
    return accepted


def get_exercise_program_for_path(program_id: int = Path(...),
                                  db: Session = Depends(get_db)):
    exists = db.query(ExerciseProgram).filter(ExerciseProgram.id==program_id).first()
    if not exists:
        raise_not_found("program is not found")
    return exists


@exercise_program_router.post("/create/{profile_id}", response_model=ExerciseProgramResponse)
def create_exercise_program(request: CreateExerciseProgram,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            athlete: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    new_program = ExerciseProgram.create(request.title_of_the_program, athlete.id, coach.id,
                                        request.purpose_of_the_program, request.start_date, request.end_date, 
                                        request.number_of_weekly_sessions,request.program_status, 
                                        request.training_days, request.general_description,
                                        request.program_version, request.coach_note)
    db.add(new_program)
    db.commit()
    db.refresh(new_program)
    return new_program


@exercise_program_router.put("/update/{program_id}", response_model=ExerciseProgramResponse)
def update_exercise_program(request: UpdateExerciseProgram,
                            db: Session = Depends(get_db),
                            athlete_id: int = Query(...),
                            current_user: User = Depends(get_current_user),
                            program: ExerciseProgram = Depends(get_exercise_program_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    athlete = get_profile_athlete(athlete_id, db)
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    program.update(request.title_of_the_program, request.purpose_of_the_program, request.start_date, request.end_date,
    request.number_of_weekly_sessions, request.program_status, request.training_days, request.general_description,
    request.program_version, request.coach_note)
    db.commit()
    db.refresh(program)
    return program


@exercise_program_router.delete("/delete/{program_id}")
def delete_program(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   athlete_id: int = Query(...),
                   program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    athlete = get_profile_athlete(athlete_id, db)
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    db.delete(program)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }


@exercise_program_router.get("/get/one/{program_id}", response_model=ExerciseProgramResponse)
def get_exercise_program_athlete(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),                    
                         program: ExerciseProgram = Depends(get_exercise_program_for_path)):
    check_admin(db, current_user, Permission.athlete)
    athlete = get_profile_athlete_with_user_id(current_user.id, db)
    if program.athlete_id != athlete.id:
        raise_bad_request("this program is not for you")
    return program                                      


@exercise_program_router.get("/get/all/for/one", response_model=ExerciseProgramResponses)
def get_all_for_one_athlete(limit: int = Query(20, ge=1, le=100),
                    offset: int = Query(0, ge=0),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    
    check_admin(db, current_user, Permission.athlete)
    athlete = get_profile_athlete_with_user_id(current_user.id, db)
    programs = db.query(ExerciseProgram).filter(ExerciseProgram.athlete_id==athlete.id)
    total = programs.count()
    items = programs.order_by(ExerciseProgram.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }



@exercise_program_router.get("/get/one/coach/{program_id}", response_model=ExerciseProgramResponse)
def get_exercise_program_coach(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),                    
                         program: ExerciseProgram = Depends(get_exercise_program_for_path)):
    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    if program.coach_id != coach.id:
        raise_bad_request("this program is not for you")
    return program  



@exercise_program_router.get("/get/all/for/one/{profile_id}", response_model=ExerciseProgramResponses)
def get_all_for_one_coach(limit: int = Query(20, ge=1, le=100),
                    offset: int = Query(0, ge=0),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    profile_thlete: ProfileAthlete = Depends(get_profile_athlete_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach.id, profile_thlete.id, db)
    programs = db.query(ExerciseProgram).filter(ExerciseProgram.athlete_id==profile_thlete.id,
                                                ExerciseProgram.coach_id==coach.id)
    total = programs.count()
    items = programs.order_by(ExerciseProgram.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }




