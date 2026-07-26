from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.Models.user.user_model import User
from core.Models.user_role.user_role_model import UserRole
from core.Models.role.role_model import Role
from core.Schemas.user.user_shemas import *
from sqlite.database import get_db
from core.security.jwt_auth import generate_access_token, generate_refresh_token, get_current_user
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found


user_route = APIRouter(prefix="/user", tags=["user"])


@user_route.post("/create", response_model=UserResponseModel)
def create_user(request: UserRegister,
                db: Session = Depends(get_db)):
    exist = db.query(User).filter(User.user_name==request.user_name).first()
    if exist:
        raise_bad_request("user is exists")
    

    new_user = User.create(request.user_name, request.first_name, request.last_name, request.number_phone)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    

    exist_role = db.query(Role).filter(Role.name=="general_visitor").first()
    if not exist_role:
        raise_not_found("role is not found")
    user_role = UserRole(role_id=exist_role.id, user_id=new_user.id)
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return new_user


@user_route.post("/login")
def login_user(request: UserLogin,
               db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.user_name==request.user_name,
                                  User.number_phone==request.number_phone).first()
    if not user:
        raise_not_found("user is not exists")

    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)

    return {
        "detail" : "user login successfully",
        "access_token" : access_token,
        "refresh_token" : refresh_token
    }