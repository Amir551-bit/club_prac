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
from controller.service.db_helper import (create_or_update_to_api_redis, commit, update, delete,
                                           commit_notification, get_for_redis)
from core.Models.notification_system.notification_system_enum import NotificationsRequiredEnum
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
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            athlete: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    check_active_coach(coach.id, db)
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    create_or_update_to_api_redis(f"lock:create_program:{current_user.id}:{athlete.id}")
    new_program = ExerciseProgram.create(request.title_of_the_program, athlete.id, coach.id,
                                            request.purpose_of_the_program, request.start_date, request.end_date, 
                                            request.number_of_weekly_sessions,request.program_status, 
                                            request.training_days, request.general_description,
                                            request.program_version, request.coach_note)
    commit(new_program, db)
    new_notification = NotificationSystem(recipient=athlete.id, title="new exercise", text=f"{request.title_of_the_program}",
                                          type=NotificationsRequiredEnum.new_training_program.value, )
    commit_notification(new_notification, db)
    return new_program



@exercise_program_router.put("/update/{program_id}", response_model=ExerciseProgramResponse)
def update_exercise_program(request: UpdateExerciseProgram,
                            db: Session = Depends(get_db),
                            athlete_id: int = Query(...),
                            current_user: User = Depends(get_current_user),
                            program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach = get_profile_coach(current_user.id, db)
    check_active_coach(coach.id, db)
    athlete = get_profile_athlete(athlete_id, db)
    accepted_coach_to_athlete(coach.id, athlete.id, db)
    create_or_update_to_api_redis(f"lock:update_program:{coach.id}:{athlete.id}")
    program.update(request.title_of_the_program, request.purpose_of_the_program, request.start_date, request.end_date,
    request.number_of_weekly_sessions, request.program_status, request.training_days, request.general_description,
    request.program_version, request.coach_note)
    update(program, db)
    new_notification = NotificationSystem(recipient=athlete.id, title="update or change exercise program", 
                                          text=request.title_of_the_program, type=NotificationsRequiredEnum.change_training_program.value)
    commit_notification(new_notification, db)
    redis_client.delete(f"cache:exercise_program:{program.id}:{current_user.id}")
    for key in redis_client.keys(f"cache:all_programs:{athlete.id}:{current_user.id}:*"):
        redis_client.delete(key)
    return program


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
    delete(program, db)
    redis_client.delete(f"cache:exercise_program:{program.id}:{current_user.id}")
    for key in redis_client.keys(f"cache:all_programs:{athlete.id}:{current_user.id}:*"):
        redis_client.delete(key)
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
    delete(program, db)
    redis_client.delete(f"cache:exercise_program:{program.id}:{current_user.id}")
    for key in redis_client.keys(f"cache:all_programs:{athlete.id}:{current_user.id}:*"):
        redis_client.delete(key)
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
    match user_role.role_id:
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            if coach_profile.id != program.coach_id:
                raise_bad_request("this program is not for you")
            check_active_coach(coach_profile.id, db)
        case 5:
            athlete = get_profile_athlete_with_user_id(current_user.id, db)
            check_active_athlete(athlete.id, db)
            if program.athlete_id != athlete.id:
                raise_bad_request("this program is not for you")
        case 1 | 2 | 3:      # or  برای true و false هستش خوب فهمیدی 
            pass
        case _:
            raise_bad_request("you have not permision")
    return get_for_redis(f"cache:exercise_program:{program.id}:{current_user.id}", ExerciseProgramResponse, program)              



@exercise_program_router.get("/get/all/{profile_id}", response_model=ExerciseProgramResponses)
def get_all_exercise_program(limit: int = Query(20, ge=1, le=100),
                             offset: int = Query(0, ge=0),
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user),
                             athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3:
            pass 
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
            check_active_coach(coach_profile.id, db)
        case 5:
            profile_athlete = get_profile_athlete_with_user_id(current_user.id, db)
            if profile_athlete.id != athlete_profile.id:
                raise_bad_request("this program is not for you")
            check_active_athlete(profile_athlete.id, db)
        case _:                         # همون معنی else رو میده فهمیدی 
            raise_bad_request("you have not permision")
    return get_for_redis(f"cache:all_programs:{athlete_profile.id}:{current_user.id}:limit:{limit}:offset:{offset}", 
                         ExerciseProgramResponses, lambda: build_get_all_program_exercise(limit, offset, athlete_profile, db))


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
    create_or_update_to_api_redis(f"create_daily_practice:{program.id}:{current_user.id}")
    new_daily_program = DailyPractice.create(program.id, request.title_session, request.day_number, request.description, request.warm_up,
                                             request.cardio, request.cool_down)
    commit(new_daily_program, db)
    return new_daily_program


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
    create_or_update_to_api_redis(f"update_daily_practice:{daily_practice.id}:{current_user.id}")
    daily_practice.update(request.title_session, request.day_number, request.description, request.warm_up, request.cardio, request.cool_down)
    update(daily_practice, db)
    redis_client.delete(f"get_one daily practice:{daily_practice.id}:{current_user.id}")
    for key in redis_client.keys(f"cache_all_daily_practice:{program.id}:{current_user.id}:*"):
        redis_client.delete(key)
    return daily_practice



@daily_practice_router.delete("/delete/{daily_practice_id}")
def delete_daily_practice(db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
                          daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    check_admin(db, current_user, Permission.coach)
    profile_coach = get_profile_coach(current_user.id, db)
    check_active_coach(profile_coach.id, db)
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.coach_id != profile_coach.id:
        raise_bad_request("this program is not for you")
    delete(daily_practice, db)
    redis_client.delete(f"get_one daily practice:{daily_practice.id}:{current_user.id}")
    for key in redis_client.keys(f"cache_all_daily_practice:{program.id}:{current_user.id}:*"):
        redis_client.delete(key)
    return {
        "detail" : "deleted successfully"
    }




@daily_practice_router.get("/get/for/one/{daily_practice_id}", response_model=ProgramDailyResponseForOne)
def get_one(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3:
            pass
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
            if program.coach_id != coach_profile.id:
                raise_bad_request("daily practice is not for you")
            check_active_coach(coach_profile.id, db)
        case 5:
            profile_athlete = get_profile_athlete_with_user_id(current_user.id, db)
            program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
            if program.athlete_id != profile_athlete.id:
                raise_bad_request("daily practice is not for you")
            check_active_athlete(profile_athlete.id, db)
        case _:
            raise_bad_request("you have not permision")
    daily_result = db.query(DailyPractice).join(ExerciseProgram).filter(DailyPractice.id==daily_practice.id).first()
    return get_for_redis(f"get_one daily practice:{daily_practice.id}:{current_user.id}", 
                         ProgramDailyResponseForOne, daily_result)



@daily_practice_router.get("/get/all/{program_id}", response_model=ProgramDailyResponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            program: ExerciseProgram = Depends(get_exercise_program_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3:
            pass
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            if coach_profile.id != program.coach_id:
                raise_bad_request("this program is not for you")
            check_active_coach(coach_profile.id, db)
        case 5:
            profile_athlete = get_profile_athlete(current_user.id, db)
            check_active_athlete(profile_athlete.id, db)
            if program.athlete_id != profile_athlete.id:
                raise_bad_request("this program is not for you")
        case _:
            raise_bad_request("you have not permision")
    return get_for_redis(f"cache_all_daily_practice:{program.id}:{current_user.id}:{limit}:{offset}", 
                  ProgramDailyResponses, lambda: build_get_all_daily_practice(limit, offset, program, db))

# Movement_Bank


@movement_bank_router.post("/create", response_model=MovementBankresponse)
def create_movement_bank(request: CreateMovementBank,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    
    check_admin(db, current_user, Permission.club_manager)
    create_or_update_to_api_redis(f"create_movement_bank:{current_user.id}:{request.english_name}")
    new_movement = MovementBank.create(request.persion_name, request.english_name, request.category, request.target_muscle, request.auxiliary_muscles,
                                            request.required_equipment, request.difficulty_level, request.description_for_move, request.executive_warnings,
                                            request.active_status, request.image, request.video_link)
    commit(new_movement)
    return new_movement



@movement_bank_router.put("/update/{movement_bank_id}", response_model=MovementBankresponse)
def update_movement_bank(request: UpdateMovementBank,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         movement_bank: MovementBank = Depends(get_movement_bank_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    create_or_update_to_api_redis(f"update_movement_bank:{current_user.id}:{movement_bank.id}")
    movement_bank.update(request.persion_name, request.english_name, request.category, request.target_muscle,
                         request.auxiliary_muscles, request.required_equipment, request.difficulty_level, request.description_for_move,
                         request.executive_warnings, request.active_status, request.image, request.video_link)
    update(movement_bank)
    redis_client.delete(f"get_one_movement:{movement_bank.id}")
    for key in redis_client.keys(f"get_all_movement_bank:*"):
        redis_client.delete(key)
    return movement_bank


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
        redis_client.delete(f"get_one_movement:{movement_bank.id}")
        for key in redis_client.keys(f"get_all_movement_bank:*"):
            redis_client.delete(key)
        return {
            "detail": "This movement is used in programs, so it was disabled instead of deleted."
        }
    else:
        delete(movement_bank)
        redis_client.delete(f"get_one_movement:{movement_bank.id}")
        for key in redis_client.keys(f"get_all_movement_bank:*"):
            redis_client.delete(key)
        return {
            "detail": "Movement deleted successfully"
        }
    

@movement_bank_router.get("/get/one/{movement_bank_id}", response_model=MovementBankresponse)
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            movement_bank: MovementBank = Depends(get_movement_bank_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3:
            pass
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            check_active_coach(coach_profile.id, db)
        case 5:
            athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
            check_active_athlete(athlete_profile.id, db)
        case _:
            raise_bad_request("you have not permission")
    return get_for_redis(f"get_one_movement:{movement_bank.id}", MovementBankresponse, movement_bank)
    



@movement_bank_router.get("/get/all", response_model=MovementBankresponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    
    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3:
            pass
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            check_active_coach(coach_profile.id, db)
        case 5:
            athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
            check_active_athlete(athlete_profile.id, db)
        case _:
            raise_bad_request("you have not permission")
    return get_for_redis(f"get_all_movement_bank:{limit}:{offset}", MovementBankresponses, 
                         lambda: build_get_all_movement_bank(limit, offset, db))


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
    create_or_update_to_api_redis(f"create_information_movement:{current_user.id}:{daily_practice.id}:{movement.id}")
    new = InformationForMovement.create(movement.id, daily_practice.id, request.move_name, request.set_number, request.number_of_repeat,
                                        request.practice_time, request.rest_time, request.tempo, request.exercise_intensity, request.display_order,
                                        request.being_a_superset_or_a_dropset, request.move_picture, request.link_video, request.suggested_weight,
                                        request.description_coach, request.alternate_move)
    commit(new, db)
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
    create_or_update_to_api_redis(f"update_information_for_movement:{current_user.id}:{movement_info.id}")
    movement_info.update(request.move_name, request.move_picture, request.link_video, request.set_number,
                        request.number_of_repeat, request.suggested_weight, request.practice_time, request.rest_time,
                        request.tempo, request.exercise_intensity,request.description_coach, request.display_order,
                        request.alternate_move, request.being_a_superset_or_a_dropset)
    update(movement_info, db)
    redis_client.delete(f"get_one_information_for_movement_with:{current_user.id}:{daily_practice.id}")
    for key in redis_client.keys(f"get_all_information_for_movement:{daily_practice.id}:{current_user.id}:*"):
        redis_client.delete(key)
    for key in redis_client.keys(f"get_information_for_movement_guide:{movement_info.id}"):
        redis_client.delete(key)
    return movement_info




@information_for_movement_router.delete("/delete/{information_movement_id}")
def delete_information_for_movement(db: Session = Depends(get_db),
                                    current_user: User = Depends(get_current_user),
                                    movement_info: InformationForMovement = Depends(get_information_for_movement_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    check_active_coach(coach_profile.id, db)
    daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).first()
    program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
    if program.coach_id != coach_profile.id:
        raise_bad_request("this program is not for you")
    delete(movement_info, db)
    redis_client.delete(f"get_one_information_for_movement_with:{current_user.id}:{daily_practice.id}")
    for key in redis_client.keys(f"get_all_information_for_movement:{daily_practice.id}:{current_user.id}:*"):
        redis_client.delete(key)
    for key in redis_client.keys(f"get_information_for_movement_guide:{movement_info.id}"):
        redis_client.delete(key)
    return {
        "detail" : "deleted successfully"
    }


@information_for_movement_router.get("/get/{daily_practice_id}", response_model=ProgramDailyWithInformationForMovement)
def get_information_movement_with_daily_practice(db: Session = Depends(get_db),
                                                 current_user: User = Depends(get_current_user),
                                                 daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3: 
            pass
        case 4:
            coach = get_profile_coach(current_user.id, db)
            check_active_coach(coach.id, db)
            program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
            accepted_coach_to_athlete(coach.id, program.athlete_id, db)
        case 5:
            athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
            program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
            if program.athlete_id != athlete_profile.id:
                raise_bad_request("this program is not for you")
        case _:
            raise_bad_request("you have not permission")
    return get_for_redis(f"get_one_information_for_movement_with:{current_user.id}:{daily_practice.id}", 
                  ProgramDailyWithInformationForMovement, lambda: build_daily_practice_with_information_practice(daily_practice))


@information_for_movement_router.get("/get/all/information/for/movement/{daily_practice_id}", response_model=InformationForMovementResponses)
def get_all_information_for_movement(limit: int = Query(20, ge=1, le=100),
                                     offset: int = Query(0, ge=0),
                                     db: Session = Depends(get_db),
                                     current_user: User = Depends(get_current_user),
                                     daily_practice: DailyPractice = Depends(get_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3:
            pass
        case 4:
            coach = get_profile_coach(current_user.id, db)
            check_active_coach(coach.id, db)
            program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
            accepted_coach_to_athlete(coach.id, program.athlete_id, db)
        case 5:
            athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
            check_active_athlete(athlete_profile.id, db)
            program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
            if program.athlete_id != athlete_profile.id:
                raise_bad_request("this program is not for you")
        case _:
            raise_bad_request("you have not permision")
    return get_for_redis(f"get_all_information_for_movement:{daily_practice.id}:{current_user.id}:{limit}:{offset}", 
                  InformationForMovementResponses, lambda: build_get_all_information_for_movement(limit, offset, daily_practice, db))


@information_for_movement_router.get("/get/all/{information_movement_id}", response_model=InformationForMovementGuideResponse)
def get_information_movement_with_movement_guide(db: Session = Depends(get_db),
                                                 current_user: User = Depends(get_current_user),
                                                 movement_info: InformationForMovement = Depends(get_information_for_movement_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3:
            pass
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            check_active_coach(coach_profile.id, db)
            daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).first()
            program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
            if program.coach_id != coach_profile.id:
                raise_bad_request("you cat not see guide movement becouse this program is not for you")
        case 5:
            athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
            check_active_athlete(athlete_profile.id, db)
            daily_practice = db.query(DailyPractice).filter(DailyPractice.id==movement_info.daily_practice_id).first()
            program = db.query(ExerciseProgram).filter(ExerciseProgram.id==daily_practice.exercise_program_id).first()
            if athlete_profile.id != program.athlete_id:
                raise_bad_request("you cat not see guide movement")                            
        case _:
            raise_bad_request("you have not permission")
    return get_for_redis(f"get_information_for_movement_guide:{movement_info.id}", 
                  InformationForMovementGuideResponse, lambda: build_information_movement(movement_info))


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
    create_or_update_to_api_redis(f"create_registration_daily_practice:{current_user.id}:{daily_practice.id}:{information_movement.id}")
    new = RegistrationDailyPractice.create(athlete_profile.id, information_movement.id, request.done_status,
                                            request.done_date, request.actual_weight_used, request.actual_number_repeat,
                                            request.difficulty_exercise, request.time_practice, request.description_for_coach,
                                            request.problem_during_exercise)
    commit(new)
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
    update(registration)
    return registration



@registration_daily_practice_router.delete("/delete/{registration_daily_practice_id}")
def delete_registration_daily_practice(db: Session = Depends(get_db),
                                       current_user: User = Depends(get_current_user),
                                       registration: RegistrationDailyPractice = Depends(get_registration_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_i:
        case 1 | 2 | 3:
            db.delete(registration)
            db.commit()
            return {
                "detail" : "deleted successfully"
            }
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            check_active_coach(coach_profile.id, db)
            accepted_coach_to_athlete(coach_profile.id, registration.athlete_id, db)
            delete(registration)
            return {
                "detail" : "deleted successfully"
            }
        case 5:
            check_admin(db, current_user, Permission.athlete)
            athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
            check_active_athlete(athlete_profile.id, db)
            if registration.athlete_id != athlete_profile.id:
                raise_bad_request("this registration is not for you")
            delete(registration)
            return {
                "detail" : "deleted successfully"
            }
        case _:
            raise_bad_request("you have not permission")


@registration_daily_practice_router.get("/get/{registration_daily_practice_id}")
def get_registration_daily_practice_router(db: Session = Depends(get_db),
                                           current_user: User = Depends(get_current_user),
                                           registration: RegistrationDailyPractice = Depends(get_registration_daily_practice_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    match user_role.role_id:
        case 1 | 2 | 3:
            return build_registration_daily_practice(registration, db)
        case 4:
            coach_profile = get_profile_coach(current_user.id, db)
            check_active_coach(coach_profile.id, db)
            athlete_profile = registration.athlete_id
            accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
            return build_registration_daily_practice(registration, db)
        case 5:
            athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
            check_active_athlete(athlete_profile.id, db)
            if registration.athlete_id != athlete_profile.id:
                raise_bad_request("this registration is not for you")
            return build_registration_daily_practice(registration, db)
        case _:
            raise_bad_request("you have not permission")







    



