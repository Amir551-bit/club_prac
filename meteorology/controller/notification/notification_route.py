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
                                        get_profile_athlete_with_user_id, get_notification_for_path, 
                                        check_active_coach, check_active_athlete, build_all_notifications_is_read,
                                        build_all_notifications_not_read)
from controller.service.db_helper import (commit, update, delete as db_delete, create_or_update_to_api_redis,
                                           get_for_redis, commit_notification )
from sqlite.redis_client import redis_client


notification_router = APIRouter(prefix="/notification", tags=["notification"])


@notification_router.post("/create/with/coach/{profile_id}", response_model=NotificationResponse)
def create_with_coach(request: CreateNotification,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user),
                      athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
    create_or_update_to_api_redis(f"create_notification_with_coach:{current_user.id}:{athlete_profile.id}")
    new_notification = NotificationSystem.create(athlete_profile.id, request.title, request.text, request.type, request.read_status)
    commit(new_notification, db)
    return new_notification



@notification_router.delete("/delete/{notification_id}")
def delete_notification(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        notification: NotificationSystem = Depends(get_notification_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    recipient_athlete_id = notification.recipient  # شناسه ورزشکار گیرنده

    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        accepted_coach_to_athlete(coach_profile.id, recipient_athlete_id, db)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if recipient_athlete_id != athlete_profile.id:
            raise_forbidden("you do not have access to this notification")
    else:
        raise_bad_request("you can not permission for delete")
        
    db_delete(notification, db)
    
    for key in redis_client.keys(f"get_all_notification_not_read:*:{recipient_athlete_id}"):
        redis_client.delete(key)
    for key in redis_client.keys(f"get_all_notification_read:*:{recipient_athlete_id}"):
        redis_client.delete(key)
        
    return {
        "detail" : "deleted successfully"
    }




@notification_router.get("/get/{notification_id}", response_model=NotificationResponse)
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            notification: NotificationSystem = Depends(get_notification_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    recipient_athlete_id = notification.recipient

    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        accepted_coach_to_athlete(coach_profile.id, recipient_athlete_id, db)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if recipient_athlete_id != athlete_profile.id:
            raise_forbidden("you do not have access to this notification")
        if notification.read_status == False:
            notification.read_notification()
            db.commit()
            db.refresh(notification)
            
        for key in redis_client.keys(f"get_all_notification_not_read:*:{recipient_athlete_id}"):
            redis_client.delete(key)
        for key in redis_client.keys(f"get_all_notification_read:*:{recipient_athlete_id}"):
            redis_client.delete(key)
    else:
        raise_bad_request("you can not permission")
        
    return notification


@notification_router.get("/all/read/{profile_id}", response_model=NotificationResponses)
def get_all_with_athlete_read(limit: int = Query(20, ge=1, le=100),
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
            raise_bad_request("notifications is not for you")
        check_active_athlete(profile_athlete.id, db)
    else:
        raise_bad_request("you have not permission")
        
    return get_for_redis(f"get_all_notification_read:{current_user.id}:{limit}:{offset}:{athlete_profile.id}",
                         NotificationResponses, lambda: build_all_notifications_is_read(limit, offset, athlete_profile, db))




@notification_router.get("/all/not/read/{profile_id}", response_model=NotificationResponses)
def get_all_with_athlete_not_read(limit: int = Query(20, ge=1, le=100),
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
            raise_bad_request("notifications is not for you")
        check_active_athlete(profile_athlete.id, db)
    else:
        raise_bad_request("you have not permission")
        
    return get_for_redis(f"get_all_notification_not_read:{current_user.id}:{limit}:{offset}:{athlete_profile.id}",
                  NotificationResponses, lambda: build_all_notifications_not_read(limit, offset, athlete_profile, db))