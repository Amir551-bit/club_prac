from fastapi import Depends, APIRouter, Path, Query
from core.Models.profile.profile_coach_model import ProfileCoach, Specialties
from core.Schemas.profile.profile_coach import *
from sqlite.database import get_db
from sqlalchemy.orm import Session
from core.security.jwt_auth import get_current_user
from core.Models.user.user_model import User
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from core.Models.role.role_model import Role
from core.Models.user_role.user_role_model import UserRole
from core.Models.role.permission import Permission
from core.security.jwt_auth import check_admin

profile_coach_router = APIRouter(prefix="/profile/coach", tags=["profile_coach"])
specialties_coach_router = APIRouter(prefix="/specialties/coach", tags=["specialties_coach"])

def get_user_for_path(user_id: int = Path(...),
                      db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.id==user_id).first()
    if not exists:
        raise_not_found("user is not exists")
    return exists


def get_profile_coach_for_path(profile_id: int = Path(...),
                               db: Session = Depends(get_db)):
    
    exists = db.query(ProfileCoach).filter(ProfileCoach.id==profile_id).first()
    if not exists:
        raise_not_found("profile coach is not found")
    return exists


def get_specialties_for_path(specialties_id: int = Path(...),
                             db: Session = Depends(get_db)):
    exists = db.query(Specialties).filter(Specialties.id==specialties_id).first()
    if not exists:
        raise_not_found("specialties is not found")
    return exists


@profile_coach_router.post("/create/{user_id}", response_model=ProfileCoachResponse)
def create_profile_coach(request: CreateProfileCoach,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         user: User = Depends(get_user_for_path)):
    
    profile_exists = db.query(ProfileCoach).filter(ProfileCoach.number_phone==request.number_phone).first()
    if profile_exists:
        raise_bad_request("profile for coach is exists")

    check_admin(db, current_user, Permission.club_manager)
    
    new_profile = ProfileCoach.create(user.id, request.first_name, request.last_name, request.number_phone, request.work_history,
                                      request.documents_and_certificates, request.area_of_activity, request.attendance_hours,
                                      request.cooperation_status, request.email, request.bio, request.social_networks)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@profile_coach_router.put("/update/{profile_id}", response_model=ProfileCoachResponse)
def update_profile_coach(request: UpdateProfileCoach,
                         db: Session = Depends(get_db),
                         cuurent_user: User = Depends(get_current_user),
                         profile: ProfileCoach = Depends(get_profile_coach_for_path)):
    
    check_admin(db, cuurent_user, Permission.club_manager)
    profile.update(request.first_name, request.last_name, request.number_phone, request.work_history, request.documents_and_certificates,
                   request.area_of_activity, request.attendance_hours, request.cooperation_status, request.email, request.bio,
                   request.social_networks)
    db.commit()
    db.refresh(profile)
    return profile


@profile_coach_router.delete("/delete/{profile_id}")
def delete_profile_coach(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         profile: ProfileCoach = Depends(get_profile_coach_for_path)):
    
    check_admin(db, current_user, Permission.club_manager)
    full_name = f"{profile.first_name} {profile.last_name}"
    db.delete(profile)
    db.commit()
    return {
        "detail" : f"{full_name} is deleted succesfully"
    }


@profile_coach_router.get("/profile/coach/{profile_id}", response_model=ProfileCoachResponse)
def get_profile_coach(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     profile: ProfileCoach = Depends(get_profile_coach_for_path)):
    
    check_admin(db, current_user, Permission.athlete)
    return profile


@profile_coach_router.get("/get/all", response_model=ProfileCoachResponses)
def get_profile_coach(db: Session = Depends(get_db),
                      limit: int = Query(20, ge=1, le=100),
                      offset: int = Query(0, ge=0),
                      current_user: User = Depends(get_current_user)):
    
    check_admin(db, current_user, Permission.athlete)
    profiles = db.query(ProfileCoach)
    total = profiles.count()
    items = profiles.order_by(ProfileCoach.id.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }



@specialties_coach_router.post("/create/{profile_id}", response_model=SpecialtiesResponse)
def create_specialties_coach(request: CreateCoachSpecialties,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user),
                             profile: ProfileCoach = Depends(get_profile_coach_for_path)):
    
    check_admin(db, current_user, Permission.club_manager)
    new = Specialties.create(profile.id, request.specialties)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@specialties_coach_router.put("/update/{specialties_id}", response_model=SpecialtiesResponse)
def update_specialties(request: UpdateCoachSpecialties,
                       db: Session = Depends(get_current_user),
                       current_user: User = Depends(get_current_user),
                       specialties: Specialties = Depends(get_specialties_for_path)):
    
    check_admin(db, current_user, Permission.club_manager)
    new_update = specialties.update(request.specialties)
    db.commit()
    db.refresh(new_update)
    return new_update


@specialties_coach_router.delete("/delete/{specialties_id}")
def delete_specialties(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user),
                       specialties: Specialties = Depends(get_specialties_for_path)):
    
    check_admin(db, current_user, Permission.club_manager)
    db.delete(specialties)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }


@specialties_coach_router.get("/get/specialties/{specialties_id}", response_model=SpecialtiesResponse)
def get_specialties(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    specialties: Specialties = Depends(get_specialties_for_path)):
    
    check_admin(db, current_user, Permission.athlete)
    return specialties


@specialties_coach_router.get("/get/all", response_model=SpecialtiesResponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    
    check_admin(db, current_user, Permission.athlete)
    specialties = db.query(Specialties)
    total = specialties.count()
    items = specialties.order_by(Specialties.id.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }



@specialties_coach_router.get("/get/with/profile/{profile_id}", response_model=SpecialtiesResponsesWithProfile)
def get_specialties_with_profile(db: Session = Depends(get_db),
                                 limit: int = Query(20, ge=1, le=100),
                                 offset: int = Query(0, ge=0),
                                 current_user: User = Depends(get_current_user),
                                 profile: ProfileCoach = Depends(get_profile_coach_for_path)):
    
    check_admin(db, current_user, Permission.athlete)
    specialties = db.query(Specialties).filter(Specialties.profile_id==profile.id)
    total = specialties.count()
    items = specialties.order_by(Specialties.id.desc()).offset(offset).limit(limit).all()
    return {
        "profile" : profile,
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }





    