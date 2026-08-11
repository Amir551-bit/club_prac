from fastapi import Depends, APIRouter, Path, Query
from core.Models.profile.profile_athlete_model import ProfileAthlete, AthleteSportsInfo 
from core.Schemas.profile.profile_athlete import *
from sqlite.database import get_db
from sqlalchemy.orm import Session
from core.security.jwt_auth import get_current_user
from core.Models.user.user_model import User
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from core.Models.role.role_model import Role
from core.Models.user_role.user_role_model import UserRole
from core.Models.role.permission import Permission
from core.security.jwt_auth import check_admin
from core.Models.notification_system.notification_system_model import NotificationSystem
from core.Models.connection_coach_to_athlete.coach_to_athlete import CoachAthleteConnection
from controller.service.services import (get_profile_athlete_for_path, get_profile_athlete_or_404, get_athlete_sport_info_for_path,
                                         get_athlete_sport_info_or_404, accepted_coach_to_athlete, get_profile_coach, get_profile_athlete_with_user_id,
                                         check_active_athlete, check_active_coach) 
from sqlite.redis_client import redis_client
from controller.service.db_helper import (commit, update, delete, create_or_update_to_api_redis, 
                                          get_for_redis, commit_notification)


def build_get_all_profile_athlete_man(limit: int, offset: int, db: Session):
    athletes = db.query(ProfileAthlete).filter(ProfileAthlete.gender==1)
    count = athletes.count()
    items = athletes.order_by(ProfileAthlete.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : count,
        "limit" : limit,
        "offset" : offset
    }



profile_athlete_route = APIRouter(prefix="/profile/athlete", tags=["profile_athlete"])
athlete_sport_info = APIRouter(prefix="/athlete/sport/info", tags=["sport_info_athlete"])
  

@profile_athlete_route.post("/create", response_model=ProfileAthleteResponse)
def create_profile_athlete(request: CreateProfileAthleteSchema,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    
    exists_user = db.query(User).filter(User.id==request.user_id).first()
    if not exists_user:
        raise_not_found("user is not found")
    exists_profile = db.query(ProfileAthlete).filter(ProfileAthlete.number_phone==request.number_phone).first()
    if exists_profile:
        raise_bad_request("profile athlete is exists")
    check_admin(db, current_user, Permission.club_manager)
    create_or_update_to_api_redis(f"create_profile_athlete:{current_user.id}:{request.user_id}")
    new_profile = ProfileAthlete.create(request.user_id, request.first_name, request.last_name,
    request.number_phone, request.date_of_birth, request.gender, request.height, request.initial_weight, request.date_of_membership, 
    request.membership_status, request.the_main_trainer, request.management_description, request.training_goal,
    request.email, request.emergency_contact_number_if_needed)
    commit(new_profile, db)
    return new_profile



@profile_athlete_route.put("/update/{profile_id}", response_model=ProfileAthleteResponse)
def update_profile_athlete(request: UpdateProfileAthlete,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user),
                           profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):
    
    check_admin(db, current_user, Permission.club_manager)
    create_or_update_to_api_redis(f"update_profile_athlete:{current_user.id}:{profile.id}")
    profile.update(request.first_name, request.last_name, request.number_phone, request.email,
                   request.date_of_birth, request.gender, request.height, request.initial_weight,
                   request.training_goal, request.date_of_membership, request.the_main_trainer,
                   request.management_description, request.emergency_contact_number_if_needed)
    update(profile, db)
    for key in redis_client.keys(f"get_all_profile_athlete_man:*"):
        redis_client.delete(key)
    redis_client.delete(f"get_one_profile_athlete:{current_user.id}:{profile.id}")
    return profile


@profile_athlete_route.put("/change/status/membership/{profile_id}", response_model=ProfileAthleteResponse)
def change_status_membership(request: ChangeStatusMembership,
                             requests: CreateNotification,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user),
                             profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    if profile.membership_status == request.status:
        raise_bad_request("You did not make any changes.")
    profile.change_membership_status(request.status)
    update(profile, db)
    redis_client.delete(f"get_one_profile_athlete:{current_user.id}:{profile.id}")
    for key in redis_client.keys(f"get_all_profile_athlete_man:*"):
        redis_client.delete(key)
    new_notif = NotificationSystem.create(profile.id, requests.type, requests.title, requests.text, requests.read_status)
    commit_notification(new_notif, db)
    return profile


@profile_athlete_route.delete("/deleted/profile/athlete/{profile_id}")
def delete_profile_athlete(db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user),
                           profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    full_name = f"{profile.first_name} {profile.last_name}"
    exists_connect_coach_to_athlete = db.query(CoachAthleteConnection).filter(
                                    CoachAthleteConnection.profile_athlete_id==profile.id).first()
    if exists_connect_coach_to_athlete:
        raise_bad_request("the athlete has coach")
    deleted_sport_info = db.query(AthleteSportsInfo).filter(AthleteSportsInfo.athlete_id==profile.id).delete(synchronize_session=False)
    delete(profile)
    redis_client.delete(f"get_one_profile_athlete:{current_user.id}:{profile.id}")
    for key in redis_client.keys(f"get_all_profile_athlete_man:*"):
        redis_client.delete(key)
    return {
        "detail" : f"{full_name} is deleted succesfully"
    }

    
@profile_athlete_route.get("/get/{profile_id}",response_model=ProfileAthleteResponse)
def get_profile_athlete(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):
    
    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        accepted_coach_to_athlete(coach_profile.id, profile.id, db)
        check_active_coach(coach_profile.id, db)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if athlete_profile.id != profile.id:
            raise_bad_request("this profile is not for you")
        check_active_athlete(athlete_profile.id, db)
    else:
        raise_bad_request("you have not permission")
    return get_for_redis(f"get_one_profile_athlete:{current_user.id}:{profile.id}", ProfileAthleteResponse, profile)


@profile_athlete_route.get("/gets/man", response_model=ProfileAthleteResponses)
def get_profile_athletes_man(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         limit: int  = Query(20, ge=1, le=100),
                         offset: int = Query(0, ge=0)):
    
    check_admin(db, current_user, Permission.athlete)
    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass
    else:
        raise_bad_request("you have not permission")
    return get_for_redis(f"get_all_profile_athlete_man:{limit}:{offset}", ProfileAthleteResponses,
                          lambda: build_get_all_profile_athlete_man(limit, offset, db))


@profile_athlete_route.get("/gets/woman", response_model=ProfileAthleteResponses)
def get_profile_athletes_woman(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         limit: int  = Query(20, ge=1, le=100),
                         offset: int = Query(0, ge=0)):
    
    check_admin(db, current_user, Permission.athlete)
    athletes = db.query(ProfileAthlete).filter(ProfileAthlete.gender==2)
    count = athletes.count()
    items = athletes.order_by(ProfileAthlete.id.desc()).offset(offset).limit(limit).all()
    
    return {
        "items" : items,
        "total" : count,
        "limit" : limit,
        "offset" : offset
    }



@profile_athlete_route.get("/gets", response_model=ProfileAthleteResponses)
def get_profile_athletes_woman(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         limit: int  = Query(20, ge=1, le=100),
                         offset: int = Query(0, ge=0)):
    
    check_admin(db, current_user, Permission.athlete)
    athletes = db.query(ProfileAthlete)
    count = athletes.count()
    items = athletes.order_by(ProfileAthlete.id.asc()).offset(offset).limit(limit).all()
    
    return {
        "items" : items,
        "total" : count,
        "limit" : limit,
        "offset" : offset
    }





@athlete_sport_info.post("/create", response_model=AthleteSportsInfoResponse)
def create_athlete_sport_info(request: CreateAthleteSportsInfo,
                              db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    
    get_profile_athlete_or_404(request.athlete_id, db)
    check_admin(db, current_user, Permission.club_manager)

    new = AthleteSportsInfo.create(request.athlete_id, request.main_goal, request.sport_level, request.workout_experience,
                                   request.weekly_sessions, request.injuries, request.movement_limitations,
                                   request.food_allergies, request.medical_explanations, request.supplements_consumed,
                                   request.coach_notes)
    db.add(new)
    db.commit()
    return new



@athlete_sport_info.put("/update/{athlete_sport_info_id}", response_model=AthleteSportsInfoResponse)
def update_athlete_sport_info(request: UpdateAthleteSportsInfo,
                              db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user),
                              sport: AthleteSportsInfo = Depends(get_athlete_sport_info_for_path)):
    
    check_admin(db, current_user, Permission.club_manager)
    sport.update(request.sport_level, request.workout_experience, request.weekly_sessions,
                       request.injuries, request.movement_limitations, request.food_allergies,
                       request.medical_explanations, request.supplements_consumed,
                       request.coach_notes)
    db.commit()
    db.refresh(sport)
    return sport


@athlete_sport_info.delete("/delete/{athlete_sport_info_id}")
def delete_athlete_sport_info(db: Session = Depends(get_db),
                              cuurent_user: User = Depends(get_current_user),
                              sport: AthleteSportsInfo = Depends(get_athlete_sport_info_for_path)):
    
    check_admin(db, cuurent_user, Permission.club_manager)
    db.delete(sport)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }



@athlete_sport_info.get("/get/athlete/sport/info", response_model=AthleteSportsInfoResponses)
def get_for_athlete_sport_info(athlete_id: int = Query(...),
                    limit: int = Query(20, ge=1, le=100),
                    offset: int = Query(0, ge=0),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):

    athlete_profile = get_profile_athlete_or_404(athlete_id, db)
    sport_info = db.query(AthleteSportsInfo).filter(AthleteSportsInfo.athlete_id==athlete_id)
    total = sport_info.count()
    items = sport_info.order_by(AthleteSportsInfo.id.desc()).offset(offset).limit(limit).all()
    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        return {
            "items" : items,
            "total" : total,
            "limit" : limit,
            "offset" : offset
        }
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
        return {
            "items" : items,
            "total" : total,
            "limit" : limit,
            "offset" : offset
        }
    elif user_role.role_id == 5:
        profile_athlete = get_profile_athlete_or_404(current_user.id, db)
        if athlete_profile.id == profile_athlete.id:
            return {
                "items" : items,
                "total" : total,
                "limit" : limit,
                "offset" : offset
            }      
    else: 
        return {
            "detail" : "you have not permission"
        }       



# @athlete_sport_info.get("/get/all", response_model=AthleteSportsInfoResponses)
# def get_all(limit: int = Query(20, ge=1, le=100),
#             offset: int = Query(0, ge=0),
#             db: Session = Depends(get_db),
#             current_user: User = Depends(get_current_user)):
    
#     check_admin(db, current_user, Permission.club_manager)
#     sport_info = db.query(AthleteSportsInfo)
#     total = sport_info.count()
#     items = sport_info.order_by(AthleteSportsInfo.id.desc()).offset(offset).limit(limit).all()
#     return {
#         "items" : items,
#         "total" : total,
#         "limit" : limit,
#         "offset" : offset
#     }


    
