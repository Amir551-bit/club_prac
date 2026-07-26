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
from core.Models.user_role.user_role_model import UserRole

exercise_program_router = APIRouter(prefix="/exercise/program", tags=["exercise_program"])
daily_practice_router = APIRouter(prefix="/daily/practice", tags=["daily_practice"])
movement_bank_router = APIRouter(prefix="/movement/bank", tags=["movement_bank"])
information_for_movement_router = APIRouter(prefix="/information/for/movement", tags=["information_for_movement"])
registration_daily_practice_router = APIRouter(prefix="/registration/daily/practice", tags=["registration_daily_practice"])


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


def get_daily_practice_for_path(daily_practice_id: int = Path(...),
                                db: Session = Depends(get_db)):
    exists = db.query(DailyPractice).filter(DailyPractice.id==daily_practice_id).first()
    if not exists:
        raise_not_found("daily practice is not found")
    return exists




def get_movement_bank_for_path(movement_bank_id: int = Path(...),
                               db: Session = Depends(get_db)):
    exists = db.query(MovementBank).filter(MovementBank.id==movement_bank_id).first()
    if not exists:
        raise_not_found("movement bank is not found")
    return exists


def get_movement_bank(movement_bank_id: int, db: Session):
    exists = db.query(MovementBank).filter(MovementBank.id==movement_bank_id).first()
    if not exists:
        raise_not_found("movement bank is not found")
    return exists


def get_information_for_movement_for_path(information_movement_id: int = Path(...),
                                 db: Session = Depends(get_db)):
    exists = db.query(InformationForMovement).filter(InformationForMovement.id==information_movement_id).first()
    if not exists:
        raise_bad_request("movement information is not found")
    return exists


def get_registration_daily_practice_for_path(registration_daily_practice_id: int = Path(...),
                                             db: Session = Depends(get_db)):

    exists = db.query(RegistrationDailyPractice).filter(RegistrationDailyPractice.id==registration_daily_practice_id).first()
    if not exists:
        raise_not_found("this not found")
    return exists


def build_daily_practice(daily_practice: DailyPractice):
    exercise_program = daily_practice.exercise_program
    return {
        "title_session" : daily_practice.title_session,
        "day_number": daily_practice.day_number,
        "description": daily_practice.description,
        "warm_up": daily_practice.warm_up,
        "cardio":  daily_practice.cardio,
        "cool_down": daily_practice.cool_down,
        "created_date": daily_practice.created_date,
        "update_date": daily_practice.update_date
    }


def build_daily_practice_with_information_practice(daily_practice: DailyPractice):
    information_movement = daily_practice.movements_info
    return {
            "title_session" : daily_practice.title_session,
            "day_number": daily_practice.day_number,
            "description": daily_practice.description,
            "warm_up": daily_practice.warm_up,
            "cardio":  daily_practice.cardio,
            "cool_down": daily_practice.cool_down,
            "created_date": daily_practice.created_date,
            "update_date": daily_practice.update_date,
            "movement_info" : information_movement
        }


def build_information_movement(information_movement: InformationForMovement):
    movement = information_movement.move_bank
    return {
        "move_name": information_movement.move_name,
        "move_picture": information_movement.move_picture,
        "link_video": information_movement.link_video,
        "set_number": information_movement.set_number,
        "number_of_repeat": information_movement.number_of_repeat,
        "suggested_weight": information_movement.suggested_weight,
        "practice_time": information_movement.practice_time,
        "rest_time": information_movement.rest_time,
        "tempo": information_movement.tempo,
        "exercise_intensity": information_movement.exercise_intensity,
        "description_coach": information_movement.description_coach,
        "display_order": information_movement.display_order,
        "alternate_move": information_movement.alternate_move,
        "being_a_superset_or_a_dropset": information_movement.being_a_superset_or_a_dropset,
        "guide_movement" : movement
    }


def build_registration_daily_practice(registration: RegistrationDailyPractice, db: Session):
    information_for_movement = registration.movements_info
    daily_practice = db.query(DailyPractice).filter(DailyPractice.id==information_for_movement.daily_practice_id).first()
    return {
        "done_status" : registration.done_status,
        "done_date" : registration.done_date,
        "actual_weight_used" : registration.actual_weight_used,
        "actual_number_repeat" : registration.actual_number_repeat,
        "difficulty_exercise" : registration.difficulty_exercise,
        "time_practice" : registration.time_practice,
        "description_for_coach" : registration.description_for_coach,
        "problem_during_exercise" : registration.problem_during_exercise,
        "information_for_movement" : information_for_movement,
        "daily_practice" : daily_practice
    }


# Exercise_Program

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


# Daily_Practice


@daily_practice_router.post("/create/{program_id}", response_model=ProgramDailyResponse)
def create_daily_practice(request: CreateProgramDaily,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          program: ExerciseProgram = Depends(get_exercise_program_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    if program.coach_id != profile_coach.id:
        raise_bad_request("this program is not for you")
    new_daily_program = DailyPractice.create(program.id, request.title_session, request.day_number, request.description, request.warm_up,
                                             request.cardio, request.cool_down)
    db.add(new_daily_program)
    db.commit()
    db.refresh(new_daily_program)
    return new_daily_program



@daily_practice_router.put("/update/{daily_practice_id}", response_model=ProgramDailyResponse)
def update_daily_practice(request: UpdateProgramDaily,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.coach_id != profile_coach.id:
        raise_bad_request("this program is not for you")
    daily_practice.update(request.title_session, request.day_number, request.description, request.warm_up, request.cardio, request.cool_down)
    db.commit()
    db.refresh(daily_practice)
    return daily_practice



@daily_practice_router.delete("/delete/{daily_practice_id}")
def delete_daily_practice(db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if not program.coach_id != profile_coach.id:
        raise_bad_request("this program is not for you")
    db.delete(daily_practice)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }



@daily_practice_router.get("/get/for/one/athlete/{daily_practice_id}")
def get_one_for_athlete(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    check_admin(db, current_user, Permission.athlete)
    profile_athlete = get_profile_athlete(current_user.id, db)
    program = db.query(ExerciseProgram).join(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if not program.athlete_id != profile_athlete.id:
        raise_bad_request("daily practice is not for you")
    return build_daily_practice(daily_practice)



@daily_practice_router.get("/get/all/for/athlete/{program_id}")
def get_all_for_athlete(limit: int = Query(20, ge=1, le=100),
                        offset: int = Query(0, ge=0),
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    check_admin(db, current_user, Permission.athlete)
    profile_athlete = get_profile_athlete(current_user.id, db)
    if program.athlete_id != profile_athlete.id:
        raise_bad_request("this program is not for you")
    daily_practices = db.query(DailyPractice).join(ExerciseProgram).filter(DailyPractice.exercise_program_id==program.id)
    total = daily_practices.count()
    items = daily_practices.order_by(DailyPractice.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "query" : [build_daily_practice(item, total) for item in items],
        "total" : total
    }


@daily_practice_router.get("/get/for/one/coach/{daily_practice_id}", response_model=ProgramDailyResponseForOne)
def get_one_for_coach(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user),
                      daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.coach_id != profile_coach.id:
        raise_bad_request("this program is not foy you")
    return {
        "daily_practice" : daily_practice,
        "exercise_program" : daily_practice.exercise_program
    }



@daily_practice_router.get("/get/all/for/coach/{program_id}", response_model=ProgramDailyResponses)
def get_all_for_coach(limit: int = Query(20, ge=1, le=100),
                      offset: int = Query(0, ge=0),
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user),
                      program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    if program.coach_id != profile_coach.id:
        raise_bad_request("this program is not for you")
    daily_practices = db.query(DailyPractice).join(ExerciseProgram).filter(DailyPractice.exercise_program_id==program.id)
    total = daily_practices.count()
    items = daily_practices.order_by(DailyPractice.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "program" : program
    }


# Movement_Bank


@movement_bank_router.post("/create", response_model=MovementBankresponse)
def create_movement_bank(request: CreateMovementBank,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    
    check_admin(db, current_user, Permission.club_manager)
    new_movement = MovementBank.create(request.persion_name, request.english_name, request.category, request.target_muscle, request.auxiliary_muscles,
                                            request.required_equipment, request.difficulty_level, request.description_for_move, request.executive_warnings,
                                            request.active_status, request.image, request.video_link)
    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)
    return new_movement



@movement_bank_router.put("/update/{movement_bank_id}", response_model=MovementBankresponse)
def update_movement_bank(request: UpdateMovementBank,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         movement_bank: MovementBank = Depends(get_movement_bank_for_path)):
    
    check_admin(db, current_user, Permission.club_manager)
    movement_bank.update(request.persion_name, request.english_name, request.category, request.target_muscle,
                         request.auxiliary_muscles, request.required_equipment, request.difficulty_level, request.description_for_move,
                         request.executive_warnings, request.active_status, request.image, request.video_link)
    db.commit()
    db.refresh(movement_bank)
    return movement_bank


@movement_bank_router.delete("/delete/{movement_bank_id}")
def delete_movement_bank(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         movement_bank: MovementBank = Depends(get_exercise_program_athlete)):

    check_admin(db, current_user, Permission.club_manager)
    db.delete(movement_bank)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }


@movement_bank_router.get("/get/one/{movement_bank_id}", response_model=MovementBankresponse)
def get_one(db: Session = Depends(get_current_user),
            current_user: User = Depends(get_current_user),
            movement_bank: MovementBank = Depends(get_exercise_program_athlete)):

    check_admin(db, current_user, Permission.athlete)
    return movement_bank


@movement_bank_router.get("/get/all", response_model=MovementBankresponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    
    check_admin(db, current_user, Permission.athlete)
    move = db.query(MovementBank)
    total = move.count()
    items = move.order_by(MovementBank.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }



# Information_For_Movement


@information_for_movement_router.post("/create/{daily_practice_id}/{movement_bank_id}", response_model=InformationForMovementResponse)
def create_information_for_movement(request: CreateInformationForMovement,
                                    db: Session = Depends(get_db),
                                    current_user: User = Depends(get_current_user),
                                    daily_practice: DailyPractice = Depends(get_daily_practice_for_path),
                                    movement: MovementBank = Depends(get_movement_bank_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.coach_id != coach_profile.id:
        raise_bad_request("this program is not for you")
    new = InformationForMovement.create(movement.id, daily_practice.id, request.move_name, request.set_number, request.number_of_repeat,
                                        request.practice_time, request.rest_time, request.tempo, request.exercise_intensity, request.display_order,
                                        request.being_a_superset_or_a_dropset, request.move_picture, request.link_video, request.suggested_weight,
                                        request.description_coach, request.alternate_move)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@information_for_movement_router.put("/update/{information_movement_id}", response_model=InformationForMovementResponse)
def update_information_for_movement(request: UpdateMovementBank,
                                    db: Session = Depends(get_db),
                                    current_user: User = Depends(get_current_user),
                                    movement_info: InformationForMovement = Depends(get_information_for_movement_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).frist()
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.id).first()
    if program.coach_id != coach_profile.id:
        raise_bad_request("this program is not for you")
    movement_info.update(request.move_name, request.move_picture, request.link_video, request.set_number,
                        request.number_of_repeat, request.suggested_weight, request.practice_time, request.rest_time,
                        request.tempo, request.exercise_intensity,request.description_coach, request.display_order,
                        request.alternate_move, request.being_a_superset_or_a_dropset)
    db.commit()
    db.refresh(movement_info)
    return movement_info
    



@information_for_movement_router.delete("/delete/{information_movement_id}")
def delete_information_for_movement(db: Session = Depends(get_db),
                                    current_user: User = Depends(get_current_user),
                                    movement_info: InformationForMovement = Depends(get_information_for_movement_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).frist()
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.id).first()
    if program.coach_id != coach_profile.id:
        raise_bad_request("this program is not for you")
    db.delete(movement_info)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }


@information_for_movement_router.get("/get/{daily_practice_id}")
def get_information_movement_with_daily_practice(db: Session = Depends(get_db),
                                                 current_user: User = Depends(get_current_user),
                                                 daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    check_admin(db, current_user, Permission.athlete)
    athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.athlete_id != athlete_profile.id:
        raise_bad_request("this program is not for you")
    return build_daily_practice_with_information_practice(daily_practice)





@information_for_movement_router.get("/get/all/{information_movement_id}")
def get_information_movement_with_movement_guide(db: Session = Depends(get_db),
                                                 current_user: User = Depends(get_current_user),
                                                 movement_info: InformationForMovement = Depends(get_information_for_movement_for_path)):

    check_admin(db, current_user, Permission.athlete)
    athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
    daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).first()
    if not daily_practice:
        raise_not_found("is not found")
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if not program:
        raise_not_found("is not found")
    if not athlete_profile.id != program.athlete_id:
        raise_bad_request("you cat not see guide movement")
    return build_information_movement(movement_info)






# Registration_Daily_Practice



@registration_daily_practice_router.post("/create/{daily_practice_id}/{information_movement_id}", response_model=RegistrationDailyPracticeResponse)
def create_registration_daily_practice(request: CreateRegistrationDailyPractice,
                                       db: Session = Depends(get_db),
                                       current_user: User = Depends(get_current_user),
                                       daily_practice: DailyPractice = Depends(get_daily_practice_for_path),
                                       information_movement: InformationForMovement = Depends(get_information_for_movement_for_path)):

    check_admin(db, current_user, Permission.athlete)
    athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
    if not information_movement.daily_practice != daily_practice.id:
        raise_bad_request("this daily pracrice is not for this information for movement")
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.athlete_id != athlete_profile.id:
        raise_bad_request("this program is not for you")
    new = RegistrationDailyPractice.create(athlete_profile.id, information_movement.id, request.done_status,
                                            request.done_date, request.actual_weight_used, request.actual_number_repeat,
                                            request.difficulty_exercise, request.time_practice, request.description_for_coach,
                                            request.problem_during_exercise)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@registration_daily_practice_router.put("/update/{registration_daily_practice_id}", response_model=RegistrationDailyPracticeResponse)
def update_registration_daily_practice(request: UpdateRegistrationDailyPractice,
                                       db: Session = Depends(get_db),
                                       current_user: User = Depends(get_current_user),
                                       registration: RegistrationDailyPractice = Depends(get_registration_daily_practice_for_path)):

    check_admin(db, current_user, Permission.athlete)
    athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
    if registration.athlete_id != athlete_profile:
        raise_bad_request("this registration is not for you")
    registration.update(request.done_status, request.done_date,request.actual_weight_used, request.actual_number_repeat, 
                        request.difficulty_exercise, request.time_practice, request.description_for_coach, request.problem_during_exercise)
    db.commit()
    db.refresh(registration)
    return registration



@registration_daily_practice_router.delete("/delete/{registration_daily_practice_id}")
def update_registration_daily_practice(db: Session = Depends(get_db),
                                       current_user: User = Depends(get_current_user),
                                       registration: RegistrationDailyPractice = Depends(get_registration_daily_practice_for_path)):

    check_admin(db, current_user, Permission.athlete)
    athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
    if not registration.athlete_id != athlete_profile:
        raise_bad_request("this registration is not for you")
    db.delete(registration)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }


@registration_daily_practice_router.get("/get/{registration_daily_practice_id}")
def get_registration_daily_practice_router(db: Session = Depends(get_db),
                                           current_user: User = Depends(get_current_user),
                                           registration: RegistrationDailyPractice = Depends(get_registration_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()

    if user_role.role_id == 3:
        return build_registration_daily_practice(registration, db)
    if user_role.role_id == 4:
        coach_profile = get_profile_athlete_with_user_id(current_user.id, db)
        athlete_profile = registration.athlete_id
        accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
        return build_registration_daily_practice(registration, db)
    if user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if registration.athlete_id != athlete_profile.id:
            raise_bad_request("this registration is not for you")
        return build_registration_daily_practice(registration, db)
        






    



