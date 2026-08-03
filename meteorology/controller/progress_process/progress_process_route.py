from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from core.security.jwt_auth import check_admin, get_current_user
from sqlite.database import get_db
from core.Models.measurement_and_progress.progress_process import ProgressPicture, ProgressProcess
from core.Schemas.progress_process_schema.progress_process_schema import *
from core.Models.user.user_model import User
from core.Models.role.permission import Permission
from core.Models.user_role.user_role_model import UserRole
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.profile.profile_coach_model import ProfileCoach
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from core.Models.connection_coach_to_athlete.coach_to_athlete import CoachAthleteConnection
from controller.service.services import (accepted_coach_to_athlete, get_profile_athlete_with_user_id, get_profile_coach,
                                         get_profile_athlete_for_path, get_progress_process_for_path, get_progress_picture_for_path,
                                         get_progress_process_and_check_athlete, get_progress_process_and_check_coach,
                                         build_progress_process, build_progress_process_all, build_progress_picture_one,
                                            )


progress_process_router = APIRouter(prefix="/progress/process", tags=["progress_process"])
progress_picture_router= APIRouter(prefix="/progress/picture", tags=["progress_picture"])
 
 

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


@progress_process_router.delete("/delete/{progress_process_id}")
def delete_progress_process(db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            progress: ProgressProcess = Depends(get_progress_process_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        db.delete(progress)
        db.commit()
        return {
            "detail" : "deleted successfully"
        }
    elif user_role.role_id == 4:
        profile_coach = get_profile_coach(current_user.id, db)
        if profile_coach.id != progress.data_recorder_coach:
            raise_bad_request("this progress process is not for you")
        db.delete(progress)
        db.commit()
        return {
            "detail" : "deleted successfully"
        }
    else:
        raise_bad_request("you have not permission")


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
    get_progress_process_and_check_coach(progress_picture, coach_profile, db)
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


