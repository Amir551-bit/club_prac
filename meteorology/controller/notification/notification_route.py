from fastapi import Depends, APIRouter, Query, Path
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from sqlite.database import get_db
from sqlalchemy.orm import Session
from core.Models.user.user_model import User
from core.Models.user_role.user_role_model import UserRole
from core.Schemas.notification_system.notification_system_schemas import *
from core.security.jwt_auth import get_current_user, check_admin
from core.Models.notification_system.notification_system_model import NotificationSystem
from controller.profile_athlete.profile_athlete_route import get_profile_athlete_for_path
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.role.permission import Permission
from controller.service.services import (accepted_coach_to_athlete, get_profile_coach, 
                                        get_profile_athlete_with_user_id, get_notification_for_path)


notification_router = APIRouter(prefix="/notification", tags=["notification"])


@notification_router.post("/create/with/coach/{profile_id}", response_model=NotificationResponse)
def create_with_coach(request: CreateNotification,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user),
                      athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
    new_notification = NotificationSystem.create(athlete_profile.id, request.title, request.text, request.type, request.read_status)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification



@notification_router.delete("/delete/{notification_id}")
def delete(db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user),
           notification: NotificationSystem = Depends(get_notification_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        db.delete(notification)
        db.commit()
        return {
            "detail" : "deleted successfully"
        }
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        athlete_profile = notification.recipient
        accepted_coach_to_athlete(coach_profile.id, athlete_profile, db)
        db.delete(notification)
        db.commit()
        return {
            "detail" : "deleted successfully"
        }
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if notification.recipient != athlete_profile.id:
            raise_forbidden("you do not have access to this notification")
        db.delete(notification)
        db.commit()
        return {
            "detail" : "deleted successfully"
        }
    else:
        raise_bad_request("you can not permission for delete")




@notification_router.get("/get/{notification_id}", response_model=NotificationResponse)
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            notification: NotificationSystem = Depends(get_notification_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 2 or user_role.role_id == 3:
        return notification
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        athlete_profile = notification.recipient
        accepted_coach_to_athlete(coach_profile.id, athlete_profile, db)
        return notification
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if notification.recipient != athlete_profile.id:
            raise_forbidden("you do not have access to this notification")
        if notification.read_status == False:
            notification.read_notification()
            db.commit()
        return notification
    else:
        raise_bad_request("you can not permission for delete")



@notification_router.get("/all/read", response_model=NotificationResponses)
def get_all_with_athlete_read(limit: int = Query(20, ge=1, le=100),
                         offset: int = Query(0, ge=0),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):

    check_admin(db, current_user, Permission.athlete)
    athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
    notifications = db.query(NotificationSystem).filter(NotificationSystem.recipient==athlete_profile.id,
                                                        NotificationSystem.read_status==True)
    total = notifications.count()
    items = notifications.order_by(NotificationSystem.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset,
        "profile_athlete" : athlete_profile
    }




@notification_router.get("/all/not/read", response_model=NotificationResponses)
def get_all_with_athlete_not_read(limit: int = Query(20, ge=1, le=100),
                         offset: int = Query(0, ge=0),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):

    check_admin(db, current_user, Permission.athlete)
    athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
    notifications = db.query(NotificationSystem).filter(NotificationSystem.recipient==athlete_profile.id,
                                                        NotificationSystem.read_status==False)
    total = notifications.count()
    items = notifications.order_by(NotificationSystem.created_date.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset,
        "profile_athlete" : athlete_profile
    }


