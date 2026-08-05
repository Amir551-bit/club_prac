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
from core.Models.notification_system.notification_system_model import NotificationSystem
from controller.service.services import check_active_coach, check_active_athlete
from controller.service.services import (get_profile_coach, get_profile_athlete_for_path, get_profile_athlete, get_profile_athlete_with_user_id,
                                         accepted_coach_to_athlete, get_exercise_program_for_path, get_daily_practice_for_path,
                                         get_information_for_movement_for_path, get_movement_bank_for_path, get_movement_bank,
                                         get_registration_daily_practice_for_path, build_daily_practice, build_daily_practice_with_information_practice,
                                         build_information_movement, build_registration_daily_practice, build_get_all_information_for_movement)
from sqlite.redis_client import redis_client
import json


exercise_program_router = APIRouter(prefix="/exercise/program", tags=["exercise_program"])
daily_practice_router = APIRouter(prefix="/daily/practice", tags=["daily_practice"])
movement_bank_router = APIRouter(prefix="/movement/bank", tags=["movement_bank"])
information_for_movement_router = APIRouter(prefix="/information/for/movement", tags=["information_for_movement"])
registration_daily_practice_router = APIRouter(prefix="/registration/daily/practice", tags=["registration_daily_practice"])


def build_get_all_program_exercise(limit: int, offset: int, athlete: ProfileAthlete, db: Session):

    programs = db.query(ExerciseProgram).filter(ExerciseProgram.athlete_id==athlete.id)
    total = programs.count()
    items = programs.order_by(ExerciseProgram.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }


def build_get_all_movement_bank(limit: int, offset: int, db: Session):

        move = db.query(MovementBank)
        total = move.count()
        items = move.order_by(MovementBank.created_date.desc()).offset(offset).limit(limit).all()
        return {
            "items" : items,
            "total" : total,
            "limit" : limit,
            "offset" : offset
        }


def build_get_all_daily_practice(limit: int, offset: int, program: ExerciseProgram, db: Session):

    daily_practices = db.query(DailyPractice).join(ExerciseProgram).filter(DailyPractice.exercise_program_id==program.id)
    total = daily_practices.count()
    items = daily_practices.order_by(DailyPractice.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : [build_daily_practice(item, total) for item in items],
        "total" : total,
        "program" : program
    }
  
# Exercise_Program

@exercise_program_router.post("/create/{profile_id}", response_model=ExerciseProgramResponse)
def create_exercise_program(request: CreateExerciseProgram,
                            requests: CreateNotification,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            athlete: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    check_active_coach(coach.id, db)
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    locked_key = f"lock:create_program:{current_user.id}:{athlete.id}"

    is_locked = redis_client.set(locked_key, "locked", ex=6, nx=True)
    if not is_locked:
        raise_bad_request("درخواست شما در حال پردازش است، لطفاً کمی صبر کنید.")
    try:
        new_program = ExerciseProgram.create(request.title_of_the_program, athlete.id, coach.id,
                                            request.purpose_of_the_program, request.start_date, request.end_date, 
                                            request.number_of_weekly_sessions,request.program_status, 
                                            request.training_days, request.general_description,
                                            request.program_version, request.coach_note)
        db.add(new_program) 
        db.commit()
        db.refresh(new_program)
        new_notification = NotificationSystem.create(athlete.id, requests.type, requests.title, requests.text,
                                                     requests.read_status)
        db.add(new_notification)
        db.commit()
        return new_program
    finally:
        pass


@exercise_program_router.put("/update/{program_id}", response_model=ExerciseProgramResponse)
def update_exercise_program(request: UpdateExerciseProgram,
                            requests: CreateNotification,
                            db: Session = Depends(get_db),
                            athlete_id: int = Query(...),
                            current_user: User = Depends(get_current_user),
                            program: ExerciseProgram = Depends(get_exercise_program_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    check_active_coach(coach.id, db)
    athlete = get_profile_athlete(athlete_id, db)
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    locked_key = f"lock:update_program:{coach.id}:{athlete.id}"
    is_locked = redis_client.set(locked_key, "locked", ex=6, nx=True)

    if not is_locked:
        raise_bad_request("درخواست شما در حال پردازش است، لطفاً کمی صبر کنید.")
    try:
        program.update(request.title_of_the_program, request.purpose_of_the_program, request.start_date, request.end_date,
        request.number_of_weekly_sessions, request.program_status, request.training_days, request.general_description,
        request.program_version, request.coach_note)
        db.commit()
        db.refresh(program)
        new_notification = NotificationSystem.create(athlete.id, requests.type, requests.title, requests.text,
                                                     requests.read_status)
        db.add(new_notification)
        db.commit()
        return program
    finally:
        pass


@exercise_program_router.delete("/delete/{program_id}")
def delete_program(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   athlete_id: int = Query(...),
                   program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    check_active_coach(coach.id, db)
    athlete = get_profile_athlete(athlete_id, db)
    if program.coach_id != coach.id:
        raise_bad_request("you have not permission for this program")
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    exists_daily_practice = db.query(DailyPractice).filter(DailyPractice.exercise_program_id==program.id).first()
    if exists_daily_practice:
        raise_bad_request("this program has daily practice")
    db.delete(program)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }


@exercise_program_router.delete("/delete/with/all/daily/practice/{program_id}")
def delete_program_with_all_daily_practice(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   athlete_id: int = Query(...),
                   program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    check_active_coach(coach.id, db)
    athlete = get_profile_athlete(athlete_id, db)
    if program.coach_id != coach.id:
        raise_bad_request("you have not permission for this program")
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    db.delete(program)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }



# @exercise_program_router.delete("/delete/{program_id}")
# def delete_program(db: Session = Depends(get_db),
#                    current_user: User = Depends(get_current_user),
#                    force_delete: bool = Query(False, description="اگر True باشد تمام تمرین‌های روزانه هم پاک می‌شوند"),
#                    program: ExerciseProgram = Depends(get_exercise_program_for_path)):

#     check_admin(db, current_user, Permission.coach)
#     coach = get_profile_coach(current_user.id, db)
    
#     if program.coach_id != coach.id:
#         raise_bad_request("you have not permission for this program")
    
#     if not force_delete:
#         exists_daily_practice = db.query(DailyPractice).filter(DailyPractice.exercise_program_id == program.id).first()
#         if exists_daily_practice:
#             raise_bad_request("this program has daily practice. use force_delete=True to delete all.")

#     db.delete(program)
#     db.commit()
    
#     return {
#         "detail": "deleted successfully"
#     }



@exercise_program_router.get("/get/one/{program_id}", response_model=ExerciseProgramResponse)
def get_exercise_program_one(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),                    
                         program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        if coach_profile.id != program.coach_id:
            raise_bad_request("this program is not for you")
        check_active_coach(coach_profile.id, db)
        
    elif user_role.role_id == 5:
        athlete = get_profile_athlete_with_user_id(current_user.id, db)
        check_active_athlete(athlete.id, db)
        if program.athlete_id != athlete.id:
            raise_bad_request("this program is not for you")
            
    elif user_role.role_id not in (1, 2, 3):
        return {"detail": "you dont have permission"}

    cache_key = f"cache:exercise_program:{program.id}"
    cached_date = redis_client.get(cache_key)
    
    if cached_date:
        return json.loads(cached_date)

    response_model_obj = ExerciseProgramResponse.model_validate(program)
    json_data = response_model_obj.model_dump_json()
    redis_client.setex(cache_key, 600, json_data)
    
    return json.loads(json_data)                  



@exercise_program_router.get("/get/all/{profile_id}", response_model=ExerciseProgramResponses)
def get_all_exercise_program(limit: int = Query(20, ge=1, le=100),
                             offset: int = Query(0, ge=0),
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user),
                             athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):
    
    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass 
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
        check_active_coach(coach_profile.id, db)
    elif user_role.role_id == 5:
        profile_athlete = get_profile_athlete_with_user_id(current_user.id, db)
        if profile_athlete.id != athlete_profile.id:
            raise_bad_request("this program is not for you")
        check_active_athlete(profile_athlete.id, db)
    else:
        return {"detail": "you dont have permission"}

    cache_key = f"cache:all_programs:{athlete_profile.id}:limit:{limit}:offset:{offset}"
    
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    programs_result = build_get_all_program_exercise(limit, offset, athlete_profile, db)

    response_model_obj = ExerciseProgramResponses.model_validate(programs_result)
    json_data = response_model_obj.model_dump_json()

    redis_client.setex(cache_key, 600, json_data)

    return json.loads(json_data)



# Daily_Practice


@daily_practice_router.post("/create/{program_id}", response_model=ProgramDailyResponse)
def create_daily_practice(request: CreateProgramDaily,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          program: ExerciseProgram = Depends(get_exercise_program_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    check_active_coach(profile_coach.id, db)
    if program.coach_id != profile_coach.id:
        raise_bad_request("this program is not for you")
    locked_key = f"create_daily_practice:{program.id}:{current_user.id}"
    is_locked = redis_client.set(locked_key, "lock", ex=6, nx=True)
    if not is_locked:
        raise_bad_request("در حال پردازش هست کمی صبر کنید")
    try:
        new_daily_program = DailyPractice.create(program.id, request.title_session, request.day_number, request.description, request.warm_up,
                                                 request.cardio, request.cool_down)
        db.add(new_daily_program)
        db.commit()
        db.refresh(new_daily_program)
        return new_daily_program
    finally:
        pass


@daily_practice_router.put("/update/{daily_practice_id}", response_model=ProgramDailyResponse)
def update_daily_practice(request: UpdateProgramDaily,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    check_active_coach(profile_coach.id, db)
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.coach_id != profile_coach.id:
        raise_bad_request("this program is not for you")
    locked_key = f"update_daily_practice:{daily_practice.id}:{current_user.id}"
    is_locked = redis_client.set(locked_key, "lock", ex=6, nx=True)
    if not is_locked:
        raise_bad_request("در حال پردازش هست کمی صبر کنید")
    try:
        daily_practice.update(request.title_session, request.day_number, request.description, request.warm_up, request.cardio, request.cool_down)
        db.commit()
        db.refresh(daily_practice)
        return daily_practice
    finally:
        pass



@daily_practice_router.delete("/delete/{daily_practice_id}")
def delete_daily_practice(db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):
    
    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    check_active_coach(profile_coach.id, db)
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if not program.coach_id != profile_coach.id:
        raise_bad_request("this program is not for you")
    db.delete(daily_practice)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }




@daily_practice_router.get("/get/for/one/{daily_practice_id}", response_model=ProgramDailyResponseForOne)
def get_one(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
        if program.coach_id != coach_profile.id:
            raise_bad_request("daily practice is not for you")
        check_active_coach(coach_profile.id, db)
    elif user_role.role_id == 5:
        profile_athlete = get_profile_athlete_with_user_id(current_user.id, db)
        program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
        if program.athlete_id != profile_athlete.id:
            raise_bad_request("daily practice is not for you")
        check_active_athlete(profile_athlete.id, db)
    else:
        return {
            "detail" : "you have not permision"
        }
    cache_key = f"get_one daily practice:{daily_practice.id}:{current_user.id}"
    cache_data = redis_client.get(cache_key)
    if cache_data:
        return json.loads(cache_data)
    daily_result = db.query(DailyPractice).join(ExerciseProgram).filter(DailyPractice.id==daily_practice.id).first()
    model_response = ProgramDailyResponseForOne.model_validate(daily_result)
    json_data = model_response.model_dump_json()
    redis_client.setex(cache_key, 600, json_data)
    return json.loads(json_data)



@daily_practice_router.get("/get/all/{program_id}", response_model=ProgramDailyResponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        if coach_profile.id != program.coach_id:
            raise_bad_request("this program is not for you")
        check_active_coach(coach_profile.id, db)
    elif user_role.role_id == 5:
        profile_athlete = get_profile_athlete(current_user.id, db)
        check_active_athlete(profile_athlete.id, db)
        if program.athlete_id != profile_athlete.id:
            raise_bad_request("this program is not for you")
    else:
        return {
            "detail" : "you have not permision"
        }
    cache_key = f"cache_all_daily_practice:{program.id}:{current_user.id}:{limit}:{offset}"
    cache_data = redis_client.get(cache_key)
    if cache_data:
        return json.loads(cache_data)
    data_result = build_get_all_daily_practice(limit, offset, program, db)
    response_model = ProgramDailyResponses.model_validate(data_result)
    model_not_json = response_model.model_dump_json()
    redis_client.setex(cache_key, 600, model_not_json)
    return json.loads(model_not_json)


# Movement_Bank


@movement_bank_router.post("/create", response_model=MovementBankresponse)
def create_movement_bank(request: CreateMovementBank,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    
    check_admin(db, current_user, Permission.club_manager)
    locked_key = f"create_movement_bank:{current_user.id}:{request.english_name}"
    is_locked = redis_client.set(locked_key, "lock", ex=6, nx=True)
    if not is_locked:
        raise_bad_request("در حال پردازش است لطفا صبور باشید.")
    try:
        new_movement = MovementBank.create(request.persion_name, request.english_name, request.category, request.target_muscle, request.auxiliary_muscles,
                                                request.required_equipment, request.difficulty_level, request.description_for_move, request.executive_warnings,
                                                request.active_status, request.image, request.video_link)
        db.add(new_movement)
        db.commit()
        db.refresh(new_movement)
        return new_movement
    finally:
        pass



@movement_bank_router.put("/update/{movement_bank_id}", response_model=MovementBankresponse)
def update_movement_bank(request: UpdateMovementBank,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         movement_bank: MovementBank = Depends(get_movement_bank_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    locked_key = f"update_movement_bank:{current_user.id}:{movement_bank.id}"
    is_locked = redis_client.set(locked_key, "lock", ex=6, nx=True)
    if not is_locked:
        raise_bad_request("در حال پردازش است لطفا صبور باشید.")
    try:
        movement_bank.update(request.persion_name, request.english_name, request.category, request.target_muscle,
                             request.auxiliary_muscles, request.required_equipment, request.difficulty_level, request.description_for_move,
                             request.executive_warnings, request.active_status, request.image, request.video_link)
        db.commit()
        db.refresh(movement_bank)
        return movement_bank
    finally:
        pass


@movement_bank_router.delete("/delete/{movement_bank_id}")
def delete_movement_bank(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         movement_bank: MovementBank = Depends(get_movement_bank_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    exists_information_for_movement = db.query(InformationForMovement).filter(
        InformationForMovement.movement_bank_id == movement_bank.id
    ).first()
    if exists_information_for_movement:
        movement_bank.active_status = ActiveStatusMovement.no.value
        db.commit()
        return {
            "detail": "This movement is used in programs, so it was disabled instead of deleted."
        }
    else:
        db.delete(movement_bank)
        db.commit()
        return {
            "detail": "Movement deleted successfully"
        }
    

@movement_bank_router.get("/get/one/{movement_bank_id}", response_model=MovementBankresponse)
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            movement_bank: MovementBank = Depends(get_movement_bank_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        check_active_coach(coach_profile.id, db)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        check_active_athlete(athlete_profile.id, db)
    else:
        return {
            "detail" : "you have not permission"
        }
    locked_key = f"get_one_movement:{movement_bank.id}"
    exists_data = redis_client.get(locked_key)
    if exists_data:
        return json.loads(exists_data)
    data = MovementBankresponse.model_validate(movement_bank)
    not_json_data = data.model_dump_json()
    redis_client.setex(locked_key, 600, not_json_data)
    return json.loads(not_json_data)
    



@movement_bank_router.get("/get/all", response_model=MovementBankresponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    
    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        check_active_coach(coach_profile.id, db)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        check_active_athlete(athlete_profile.id, db)
    else:
        return {
            "detail" : "you have not permission"
        }                                       

    locked_key = f"get_all_movement_bank:{limit}:{offset}"
    exists = redis_client.get(locked_key)
    if exists:
        return json.loads(exists)
    cache_data = build_get_all_movement_bank(limit, offset, db)
    responses = MovementBankresponses.model_validate(cache_data)
    responses_not_json = responses.model_dump_json()
    redis_client.setex(locked_key, 600, responses_not_json)
    return json.loads(responses_not_json)


# Information_For_Movement


@information_for_movement_router.post("/create/{daily_practice_id}/{movement_bank_id}", response_model=InformationForMovementResponse)
def create_information_for_movement(request: CreateInformationForMovement,
                                    db: Session = Depends(get_db),
                                    current_user: User = Depends(get_current_user),
                                    daily_practice: DailyPractice = Depends(get_daily_practice_for_path),
                                    movement: MovementBank = Depends(get_movement_bank_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    check_active_coach(coach_profile.id, db)
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
    check_active_coach(coach_profile.id, db)
    daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).first()
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.coach_id != coach_profile.id:
        raise_bad_request("this program is not for you")
    movement_info.update(request.move_name, request.move_picture, request.link_video, request.set_number,
                        request.number_of_repeat, request.suggested_weight, request.practice_time, request.rest_time,
                        request.tempo, request.exercise_intensity,request.description_coach, request.display_order,
                        request.alternate_move, request.being_a_superset_or_a_dropset)
    db.commit()

    return movement_info
    



@information_for_movement_router.delete("/delete/{information_movement_id}")
def delete_information_for_movement(db: Session = Depends(get_db),
                                    current_user: User = Depends(get_current_user),
                                    movement_info: InformationForMovement = Depends(get_information_for_movement_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    check_active_coach(coach_profile.id, db)
    daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).first()
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

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):   
        return build_daily_practice_with_information_practice(daily_practice)
    elif user_role.role_id == 4:
        coach = get_profile_coach(current_user.id, db)
        check_active_coach(coach.id, db)
        program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
        accepted_coach_to_athlete(coach.id, program.athlete_id, db)
        return build_daily_practice_with_information_practice(daily_practice)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
        if program.athlete_id != athlete_profile.id:
            raise_bad_request("this program is not for you")
        return build_daily_practice_with_information_practice(daily_practice)
    else:
        return {
            "detail" : "you have not permission"
        }



@information_for_movement_router.get("/get/all/information/for/movement/{daily_practice_id}", response_model=InformationForMovementResponses)
def get_all_information_for_movement(limit: int = Query(20, ge=1, le=100),
                                     offset: int = Query(0, ge=0),
                                     db: Session = Depends(get_db),
                                     current_user: User = Depends(get_current_user),
                                     daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        return build_get_all_information_for_movement(limit, offset, daily_practice, db)
    elif user_role.role_id == 4:
        coach = get_profile_coach(current_user.id, db)
        check_active_coach(coach.id, db)
        program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
        accepted_coach_to_athlete(coach.id, program.athlete_id, db)
        return build_get_all_information_for_movement(limit, offset, daily_practice, db)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        check_active_athlete(athlete_profile.id, db)
        program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
        if program.athlete_id != athlete_profile.id:
            raise_bad_request("this program is not for you")
        return build_get_all_information_for_movement(limit, offset, daily_practice, db)
    else:
        return {
            "detail" : "you have not permision"
        }




@information_for_movement_router.get("/get/all/{information_movement_id}")
def get_information_movement_with_movement_guide(db: Session = Depends(get_db),
                                                 current_user: User = Depends(get_current_user),
                                                 movement_info: InformationForMovement = Depends(get_information_for_movement_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        return build_information_movement(movement_info)
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        check_active_coach(coach_profile.id, db)
        daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).first()
        program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
        if program.coach_id != coach_profile.id:
            raise_bad_request("you cat not see guide movement becouse this program is not for you")
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        check_active_athlete(athlete_profile.id, db)
        daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).first()
        program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
        if athlete_profile.id != program.athlete_id:
            raise_bad_request("you cat not see guide movement")
        return build_information_movement(movement_info)
    else:
        return {
            "detail" : "you have not permission"
        }





# Registration_Daily_Practice



@registration_daily_practice_router.post("/create/{daily_practice_id}/{information_movement_id}", response_model=RegistrationDailyPracticeResponse)
def create_registration_daily_practice(request: CreateRegistrationDailyPractice,
                                       db: Session = Depends(get_db),
                                       current_user: User = Depends(get_current_user),
                                       daily_practice: DailyPractice = Depends(get_daily_practice_for_path),
                                       information_movement: InformationForMovement = Depends(get_information_for_movement_for_path)):

    check_admin(db, current_user, Permission.athlete)
    athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
    check_active_athlete(athlete_profile.id, db)
    if information_movement.daily_practice != daily_practice.id:
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
    check_active_athlete(athlete_profile.id, db)
    if registration.athlete_id != athlete_profile.id:
        raise_bad_request("this registration is not for you")
    registration.update(request.done_status, request.done_date,request.actual_weight_used, request.actual_number_repeat, 
                        request.difficulty_exercise, request.time_practice, request.description_for_coach, request.problem_during_exercise)
    db.commit()
    db.refresh(registration)
    return registration



@registration_daily_practice_router.delete("/delete/{registration_daily_practice_id}")
def delete_registration_daily_practice(db: Session = Depends(get_db),
                                       current_user: User = Depends(get_current_user),
                                       registration: RegistrationDailyPractice = Depends(get_registration_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
            db.delete(registration)
            db.commit()
            return {
                "detail" : "deleted successfully"
            }   
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        check_active_coach(coach_profile.id, db)
        accepted_coach_to_athlete(coach_profile.id, registration.athlete_id, db)
        db.delete(registration)
        db.commit()
        return {
            "detail" : "deleted successfully"
        }
    else:
        check_admin(db, current_user, Permission.athlete)
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        check_active_athlete(athlete_profile.id, db)
        if registration.athlete_id != athlete_profile.id:
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
        coach_profile = get_profile_coach(current_user.id, db)
        check_active_coach(coach_profile.id, db)
        athlete_profile = registration.athlete_id
        accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
        return build_registration_daily_practice(registration, db)
    if user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        check_active_athlete(athlete_profile.id, db)
        if registration.athlete_id != athlete_profile.id:
            raise_bad_request("this registration is not for you")
        return build_registration_daily_practice(registration, db)
        






    



