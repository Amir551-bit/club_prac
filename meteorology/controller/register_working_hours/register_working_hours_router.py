from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from sqlite.database import get_db
from core.security.jwt_auth import get_current_user, check_admin
from core.execptions.execption import raise_not_found, raise_bad_request
from core.Models.role.permission import Permission
from core.Models.user.user_model import User
from core.Models.user_role.user_role_model import UserRole
from core.Models.register_working_hours.register_working_hours import RegisterWorkingHours
from core.Schemas.register_working_hours.register_working_hours import *
from datetime import date, datetime, timezone
from core.Models.register_working_hours.register_working_hours_enum import StatusOpenning




register_working_hour_router = APIRouter(prefix="/register/working/hour", tags=["register_working_hour"])


def get_register_working_hour_for_path(register_id: int = Path(...),
                                       db: Session = Depends(get_db)):

    exists = db.query(RegisterWorkingHours).filter(RegisterWorkingHours.id==register_id).first()
    if not exists:
        raise_not_found("this is not found")
    return exists


@register_working_hour_router.post("/create", response_model=RegisterWorkingHoursResponse)
def create(request: CreateRegisterWorkingHours,
           db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):

    check_admin(db, current_user, Permission.club_manager)
    new = RegisterWorkingHours.create(request.day_date, request.start_morning, request.stop_afternoon, request.start_afternoon,
                                      request.stop_night, request.status_openning, request.title, request.message)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@register_working_hour_router.put("/update/{register_id}", response_model=RegisterWorkingHoursResponse)
def update(request: UpdateRegisterWorkingHours,
           db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user),
           register: RegisterWorkingHours =Depends(get_register_working_hour_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    register.update(request.day_date, request.start_morning, request.stop_afternoon, request.start_afternoon, request.stop_night,
                    request.status_openning, request.title, request.message)
    db.commit()
    db.refresh(register)
    return register



@register_working_hour_router.delete("/delete/{register_id}")
def delete(db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user),
           register: RegisterWorkingHours =Depends(get_register_working_hour_for_path)):

    check_admin(db, current_user, Permission.club_manager)
    db.delete(register)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }


@register_working_hour_router.get("/get/{register_id}")
def get(db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        register: RegisterWorkingHours =Depends(get_register_working_hour_for_path)):

    time_now = datetime.now().time()
    date_now = date.today()
    if register.day_date < date_now:
        raise_bad_request("تاریخ این دیکه گذشته است.")


    is_in_morning = register.start_morning <= time_now <= register.stop_afternoon
    is_in_afternoon = register.start_afternoon <= time_now <= register.stop_night
    if is_in_afternoon or is_in_morning:
        return {
            "status": StatusOpenning.is_open,
            "title": "است باز باشگاه",
            "message":" هستیم فعال ۲۳ امروز تا ساعت",
            "next_change_at": "..."
                }
    else:
        return {
        "status": StatusOpenning.closed,
        "title": "باشکاه بسته هست",
        "message":"کیرم دهنت",
        "next_change_at": "..."
            }

    