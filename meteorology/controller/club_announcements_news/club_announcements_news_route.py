from fastapi import Depends, Query, Path, APIRouter
from core.security.jwt_auth import check_admin,  get_current_user
from core.Models.club_announcements_and_news.club_announcements_news_model import ClubAnnouncementsNews
from core.Schemas.club_announcements_news.club_announcements_news_schemas import *
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from core.Models.user.user_model import User
from core.Models.user_role.user_role_model import UserRole
from sqlalchemy.orm import Session
from sqlite.database import get_db
from core.Models.role.permission import Permission
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.profile.profile_coach_model import ProfileCoach
from controller.exercise_program_route.exercise_program_route import accepted_coach_to_athlete, get_profile_coach, get_profile_athlete_with_user_id



club_announcements_news_router = APIRouter(prefix="/club/announcements/news", tags=["club_announcements_new"])


def get_club_announcements_news_for_path(club_announcements_news_id: int = Path(...),
                                         db: Session = Depends(get_db)):

    exists = db.query(ClubAnnouncementsNews).filter(ClubAnnouncementsNews.id==club_announcements_news_id).first()
    if not exists:
        raise_not_found("this is not found")
    return exists



@club_announcements_news_router.post("/create", response_model=ClubAnnouncementsNewResponse)
def create(request: CreateClubAnnouncementsNew,
           db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    
    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if not (user_role.role_id == 1 or user_role.role_id == 2 or user_role.role_id == 3 or user_role.role_id == 4):
        raise_bad_request("you have not permission")

    new = ClubAnnouncementsNews.create(request.title, request.text, request.image, request.notification_type,
                                       request.importance, request.audience, request.publication_date, request.expiration_date,
                                       request.release_status, current_user.id, request.show_on_home_page, request.public_display)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new



@club_announcements_news_router.put("/update/{club_announcements_news_id}", response_model=ClubAnnouncementsNewResponse)
def update(request: UpdateClubAnnouncementsNew,
           db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user),
           club_noti: ClubAnnouncementsNews = Depends(get_club_announcements_news_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if not (user_role.role_id == 2 or user_role.role_id == 3 or club_noti.author == current_user.id):
        raise_bad_request("validation problem")
    club_noti.update(request.title, request.text, request.image, request.notification_type, request.importance,
                     request.audience, request.publication_date, request.expiration_date, request.release_status,
                     request.show_on_home_page, request.public_display)
    db.commit()
    db.refresh(club_noti)
    return club_noti



@club_announcements_news_router.delete("/delete/{club_announcements_news_id}")
def delete(db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user),
           club_noti: ClubAnnouncementsNews = Depends(get_club_announcements_news_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if not (user_role.role_id == 2 or user_role.role_id == 3 or club_noti.author == current_user.id):
        raise_bad_request("validation problem")
    db.delete(club_noti)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }



@club_announcements_news_router.get("/one/{club_announcements_news_id}", response_model=ClubAnnouncementsNewResponse)
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            club_noti: ClubAnnouncementsNews = Depends(get_club_announcements_news_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if club_noti.audience == 2 or club_noti.audience == 1:
        return club_noti
    elif club_noti.audience == 3:
        if user_role.role_id == 4 or user_role.role_id == 3 or user_role.role_id == 2:
            return club_noti
    elif club_noti.audience == 4:
        if club_noti.author == current_user.id or user_role.role_id == 3 or user_role.role_id == 2:
            return club_noti
        else:
            user_coach = club_noti.author
            coach_profile = get_profile_coach(user_coach, db)
            athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
            accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
            return club_noti
    else:
        return {
            "detail" : "this announcement is not for you"
        }





