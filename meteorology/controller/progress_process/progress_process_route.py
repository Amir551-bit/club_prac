from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from core.security.jwt_auth import check_admin, get_current_user
from sqlite.database import get_db
from core.Models.measurement_and_progress.progress_process import ProgressPicture, ProgressProcess
from core.Schemas.progress_process_schema.progress_process_schema import *
from core.Models.user.user_model import User
from core.Models.role.permission import Permission
from core.Models.user_role.user_role_model import UserRole
from controller.exercise_program_route.exercise_program_route import (accepted_coach_to_athlete, get_profile_athlete_with_user_id,
                                                                      get_profile_athlete, get_profile_coach, get_profile_athlete_for_path)
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.profile.profile_coach_model import ProfileCoach
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from core.Models.connection_coach_to_athlete.coach_to_athlete import CoachAthleteConnection


progress_process_router = APIRouter(prefix="/progress/process", tags=["progress_process"])
progress_picture_router= APIRouter(prefix="/progress/picture", tags=["progress_picture"])


def get_progress_process_for_path(progress_process_id: int = Path(...),
                                  db: Session = Depends(get_db)):

    exists = db.query(ProgressProcess).filter(ProgressProcess.id==progress_process_id).first()
    if not exists:
        raise_not_found("this not found")
    return exists


def get_progress_picture_for_path(progress_picture_id: int = Path(...),
                         db: Session = Depends(get_db)):

    exists = db.query(ProgressPicture).filter(ProgressPicture.id==progress_picture_id).first()
    if not exists:
        raise_not_found("this not found")
    return exists


def get_progress_process_and_check_coach(progress_picture: ProgressPicture, coach_profile: ProfileCoach, db: Session):
    progress_process = db.query(ProgressProcess).filter(ProgressProcess.id==progress_picture.progress_process_id).first()
    if progress_process.data_recorder_coach != coach_profile.id:
        raise_bad_request("identification error")
    return progress_process


def get_progress_process_and_check_athlete(progress_picture: ProgressPicture, athlete_profile: ProfileAthlete, db: Session):
    progress_process = db.query(ProgressProcess).filter(ProgressProcess.id==progress_picture.progress_process_id).first()
    if progress_process.athlete_id != athlete_profile.id:
        raise_bad_request("identification error")
    return progress_process


def build_progress_process(progress_process: ProgressProcess):
    athlete_profile = progress_process.athlete
    return {
        "athlete_id" : progress_process.athlete_id,
        "date_measurement" : progress_process.date_measurement,
        "data_recorder_coach" : progress_process.data_recorder_coach,
        "weight" : progress_process.weight,
        "fat_percentage" : progress_process.fat_percentage,
        "around_neck" : progress_process.around_neck,
        "around_chest" : progress_process.around_chest,
        "around_arm" : progress_process.around_arm,
        "waist_circumference" : progress_process.waist_circumference,
        "abdominal_circumference" : progress_process.abdominal_circumference,
        "around_thigh" : progress_process.around_thigh,
        "leg_circumference" : progress_process.leg_circumference,
        "description" : progress_process.description,
        "created_date" : progress_process.created_date,
        "update_date" : progress_process.update_date,
        "athlete_profile" : athlete_profile
    }


def build_progress_process_all(profile_athlete: ProfileAthlete, limit: int, offset: int, db: Session):

    progress_process = db.query(ProgressProcess).filter(ProgressProcess.athlete_id==profile_athlete.id)
    coach_to_athlete = db.query(CoachAthleteConnection).filter(CoachAthleteConnection.profile_athlete_id==profile_athlete.id).first()
    profile_coach = coach_to_athlete.coach
    total = progress_process.count()
    items = progress_process.order_by(ProgressProcess.created_date.asc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset,
        "profile_athlete" : profile_athlete,
        "profile_coach" : profile_coach
    }




def build_progress_picture_one(progress_picture: ProgressPicture):
    progress_process = progress_picture.progress
    return {
       "progress_process_id" : progress_picture.progress_process_id,
       "date_registration" : progress_picture.date_registration,
       "front_view" : progress_picture.front_view,
       "side_view" : progress_picture.side_view,
       "back_view" :  progress_picture.back_view,
       "description" : progress_picture.description,
       "data_recorder_coach" : progress_picture.data_recorder_coach,
       "data_recorder_athlete" : progress_picture.data_recorder_coach,
       "progress_process" : progress_process
    }




@progress_process_router.post("/create/{profile_id}", response_model=ProgressProcessResponse)
def create_progress_process(request: CreateProgressProcess,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
    new = ProgressProcess.create(athlete_profile.id, request.date_measurement, coach_profile.id, request.weight, request.fat_percentage,
                                 request.around_neck, request.around_chest, request.around_arm, request.waist_circumference,
                                 request.abdominal_circumference, request.around_thigh, request.leg_circumference, request.description)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@progress_process_router.put("/update/{progress_process_id}", response_model=ProgressProcessResponse)
def update_progress_process(request: UpdateProgressProcess,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            progress_process: ProgressProcess = Depends(get_progress_process_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach_profile.id, progress_process.athlete_id, db)
    progress_process.update(request.date_measurement, request.weight, request.fat_percentage, request.around_neck, 
                            request.around_chest, request.around_arm, request.waist_circumference,request.abdominal_circumference,
                            request.around_thigh, request.leg_circumference, request.description)
    db.commit()
    db.refresh(progress_process)
    return progress_process




@progress_process_router.get("/get/one/{progress_process_id}", response_model=ProgressProcessResponseForOne)
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            progress_process: ProgressProcess = Depends(get_progress_process_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        return build_progress_process(progress_process)
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        if coach_profile.id != progress_process.data_recorder_coach:
            raise_bad_request("this is not for you")
        return build_progress_process(progress_process)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if athlete_profile.id != progress_process.athlete_id:
            raise_bad_request("this is not for you")
        return build_progress_process(progress_process)
    else:
        return {
            "detail" : "you have not access"
        }


@progress_process_router.get("/get/all/{profile_id}", response_model=ProgressProcessResponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            profile_athlete: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        return build_progress_process_all(profile_athlete, limit, offset, db)
    elif user_role.role_id == 4:
        profile_coach = get_profile_coach(current_user.id, db)
        accepted_coach_to_athlete(profile_coach.id, profile_athlete.id, db)
        return build_progress_process_all(profile_athlete, limit, offset, db)
    elif user_role.role_id == 5:
        athlete_prof = get_profile_athlete_with_user_id(current_user.id, db)
        if athlete_prof.id != profile_athlete.id:
            raise_bad_request("identification error")
        return build_progress_process_all(profile_athlete, limit, offset, db)
    else:
        return {
            "detail" : "you have not access"
        }




# progress_picture

@progress_picture_router.post("/create/{progress_process_id}", response_model=ProgressPictureResponse)
def create_progress_picture(request: CreateProgressPicture,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            progress_process: ProgressProcess = Depends(get_progress_process_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        if coach_profile.id != progress_process.data_recorder_coach:
            raise_bad_request("identification error")
        new = ProgressPicture.create_for_coach(progress_process.id, coach_profile.id, request.date_registration, request.front_view, 
                                               request.side_view, request.back_view, request.description)
        db.add(new)
        db.commit()
        db.refresh(new)
        return new
    else:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if athlete_profile.id != progress_process.athlete_id:
            raise_bad_request("identification error")
        new = ProgressPicture.create_for_athlete(progress_process.id, athlete_profile.id, request.date_registration, request.front_view, 
                                                 request.side_view, request.back_view, request.description)
        db.add(new)
        db.commit()
        db.refresh(new)
        return new


@progress_picture_router.put("/update/{progress_picture_id}", response_model=ProgressPictureResponse)
def update_progress_picture(request: UpdateProgressPicture,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            progress_picture: ProgressPicture = Depends(get_progress_picture_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    progress_process = get_progress_process_and_check_coach(progress_picture, coach_profile, db)
    progress_picture.update(request.date_registration, request.front_view, request.side_view, request.back_view, request.description)
    db.commit()
    db.refresh(progress_picture)
    return progress_picture


@progress_picture_router.delete("/delete/{progress_picture_id}")
def delete_progress_picture(db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            progress_picture: ProgressPicture = Depends(get_progress_picture_for_path)):

    
    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    progress_process = get_progress_process_and_check_coach(progress_picture, coach_profile, db)
    db.delete(progress_picture)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }



@progress_picture_router.get("/get/one/{progress_picture_id}", response_model=ProgressPictureResponseOne)
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            progress_picture: ProgressPicture = Depends(get_progress_picture_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        return build_progress_picture_one(progress_picture)
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        get_progress_process_and_check_coach(progress_picture, coach_profile, db)
        return build_progress_picture_one(progress_picture)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        get_progress_process_and_check_athlete(progress_picture, athlete_profile, db)
        return build_progress_picture_one(progress_picture)
    else:
        return {
            "detail" : "you have not access"
        }


