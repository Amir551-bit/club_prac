from fastapi import APIRouter, Depends, Path, Query
from core.Models.connection_coach_to_athlete.coach_to_athlete import CoachAthleteConnection
from core.Schemas.coach_to_athlete.coach_to_athlete_schemas import *
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.profile.profile_coach_model import ProfileCoach
from sqlalchemy.orm import Session
from sqlite.database import get_db
from core.execptions.execption import raise_not_found, raise_bad_request, raise_forbidden
from core.Models.user.user_model import User
from core.security.jwt_auth import check_admin, get_current_user
from core.Models.role.permission import Permission
from core.Schemas.profile.profile_athlete import ProfileAthleteResponse
from controller.profile_coach.profile_coach_route import get_profile_coach_for_path


coach_to_athlete_router = APIRouter(prefix="/coach/to/athlete", tags=["coach_to_athlete"])


def get_profile_athlete_or_404(profile_id: int,
                                 db: Session = Depends(get_db)):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.id==profile_id).first()
    if not exists:
        raise_not_found("profile is not found")
    return exists

def get_profile_coach_or_404(profile_id: int,
                               db: Session = Depends(get_db)):
    
    exists = db.query(ProfileCoach).filter(ProfileCoach.id==profile_id).first()
    if not exists:
        raise_not_found("profile coach is not found")
    return exists


def get_coach_to_athlete_for_path(id: int = Path(...),
                                  db: Session = Depends(get_db)):

    exists = db.query(CoachAthleteConnection).filter(CoachAthleteConnection.id==id).first()
    if not exists:
        raise_not_found("is not found")
    return exists


def build_get_response_coach_to_athlete(connect: CoachAthleteConnection):

    profile =  connect.athlete
    return {
        "profile_coach_id": connect.profile_coach_id,
        "profile_athlete_id": connect.profile_athlete_id,
        "start_date": connect.start_date,
        "status": connect.status,
        "coach_role": connect.coach_role,
        "manager_notes": connect.manager_notes,
        "end_date": connect.end_date,
        "profile_athlete" : profile
    }


@coach_to_athlete_router.post("/create", response_model=CoachToAthleteResponse)
def create_coach_to_athlete(request: CreateCoachToAthlete,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):

    check_admin(db, current_user, Permission.club_manager)
    athlete = get_profile_athlete_or_404(request.profile_athlete_id, db)
    coach = get_profile_coach_or_404(request.profile_coach_id, db)
    exists = db.query(CoachAthleteConnection).filter(CoachAthleteConnection.profile_coach_id == coach.id,
                                                     CoachAthleteConnection.profile_athlete_id == athlete.id,
                                                     CoachAthleteConnection.status == 1).first()
    if exists:
        raise_bad_request("this is a exists")

    added = CoachAthleteConnection.create(db, coach.id, athlete.id, request.start_date, request.status,
                                          request.coach_role, request.manager_notes, request.end_date)
    db.add(added)
    db.commit()
    db.refresh(added)
    return added


@coach_to_athlete_router.put("/update/{id}", response_model=CoachToAthleteResponse)
def update_coach_to_athlete(request: UpdateCoachToAthlete,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            connect: CoachAthleteConnection = Depends(get_coach_to_athlete_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    connect.update(request.start_date, request.status, request.coach_role, request.manager_notes, request.end_date)
    db.commit()
    db.refresh(connect)
    return connect



@coach_to_athlete_router.delete("/delete/{id}")
def delete_coach_to_athlete(db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            connect: CoachAthleteConnection = Depends(get_coach_to_athlete_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    fullname_athlete = f"{connect.athlete.first_name} {connect.athlete.last_name}"
    fullname_coach = f"{connect.coach.first_name} {connect.coach.last_name}"
    db.delete(connect)
    db.commit()
    return {
        "detail" : f"ahtlete {fullname_athlete} for coach {fullname_coach} is deleted"
    }




@coach_to_athlete_router.get("/get/with/profile/{profile_id}")
def get_with_profile(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    limit: int = Query(20, ge=1, le=100),
                    offset: int = Query(0, ge=0),
                    profile_coach: ProfileCoach = Depends(get_profile_coach_for_path)):

    check_admin(db, current_user, Permission.athlete)
    coach_to_athlete = db.query(CoachAthleteConnection).join(
        ProfileAthlete).filter(CoachAthleteConnection.profile_coach_id==profile_coach.id)
    
    items = coach_to_athlete.order_by(CoachAthleteConnection.id.desc()).offset(offset).limit(limit).all()
    return [build_get_response_coach_to_athlete(item) for item in items]



@coach_to_athlete_router.get("/get/all", response_model=CoachToAthleteResponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):

    check_admin(db, current_user, Permission.club_manager)
    query = db.query(CoachAthleteConnection)
    total = query.count()
    items = query.order_by(CoachAthleteConnection.id.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }





    



