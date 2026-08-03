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
                                         get_athlete_sport_info_or_404, accepted_coach_to_athlete, get_profile_coach) 

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
    new_profile = ProfileAthlete.create(user_id=request.user_id,first_name=request.first_name,last_name=request.last_name,
    number_phone=request.number_phone,date_of_birth=request.date_of_birth,gender=request.gender,height=request.height,
    initial_weight=request.initial_weight,date_of_membership=request.date_of_membership,  membership_status=request.membership_status,    
    the_main_trainer=request.the_main_trainer, management_description=request.management_description,training_goal=request.training_goal,
    email=request.email,emergency_contact_number_if_needed=request.emergency_contact_number_if_needed)

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile



@profile_athlete_route.put("/update/{profile_id}", response_model=ProfileAthleteResponse)
def update_profile_athlete(request: UpdateProfileAthlete,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user),
                           profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):
    
    check_admin(db, current_user, Permission.club_manager)
    profile.update(request.first_name, request.last_name, request.number_phone, request.email,
                   request.date_of_birth, request.gender, request.height, request.initial_weight,
                   request.training_goal, request.date_of_membership, request.the_main_trainer,
                   request.management_description, request.emergency_contact_number_if_needed)
    db.commit()
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
    db.commit()
    db.refresh(profile)
    new_notif = NotificationSystem.create(profile.id, requests.type, requests.title, requests.text, requests.read_status)
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)
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
    db.delete(profile)
    db.commit()
    return {
        "detail" : f"{full_name} is inactive succesfully"
    }

    
@profile_athlete_route.get("/get/{profile_id}",response_model=ProfileAthleteResponse)
def get_profile_athlete(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):
    
    check_admin(db, current_user, Permission.athlete)
    return profile


@profile_athlete_route.get("/gets/man", response_model=ProfileAthleteResponses)
def get_profile_athletes_man(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         limit: int  = Query(20, ge=1, le=100),
                         offset: int = Query(0, ge=0)):
    
    check_admin(db, current_user, Permission.athlete)
    athletes = db.query(ProfileAthlete).filter(ProfileAthlete.gender==1)
    count = athletes.count()
    items = athletes.order_by(ProfileAthlete.id.desc()).offset(offset).limit(limit).all()

    return {
        "items" : items,
        "total" : count,
        "limit" : limit,
        "offset" : offset
    }


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


    
