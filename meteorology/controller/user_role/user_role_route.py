from fastapi import APIRouter, Depends, Path, Query
from core.Models.user_role.user_role_model import UserRole
from core.Models.role.role_model import Role
from core.Models.user.user_model import User
from core.Schemas.user_role.user_role_schemas import *
from core.security.jwt_auth import get_current_user, check_admin
from core.execptions.execption import raise_bad_request, raise_not_found, raise_forbidden
from core.Models.role.permission import Permission
from sqlite.database import get_db
from sqlalchemy.orm import Session
from controller.service.services import get_user_for_path, build_for_user_role, get_user_role_or_404


user_role_router = APIRouter(prefix="/user/role", tags=["user_role"])

 
@user_role_router.put("/update/{user_id}", response_model=UserRoleResponse)
def update_user_role(request: UpdateUserRole,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    user: User = Depends(get_user_for_path)):
    
    check_admin(db, current_user, Permission.club_owner)
    user_role = get_user_role_or_404(user.id, db)
    user_role.update(request.role_id)
    db.commit()
    db.refresh(user_role)
    return user_role


@user_role_router.get("/get/all")
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):

    check_admin(db, current_user, Permission.club_owner)
    user_role = db.query(UserRole).join(User).join(Role)
    total = user_role.count()
    items = user_role.order_by(UserRole.id.desc()).offset(offset).limit(limit).all()
    return {
        "items" : [build_for_user_role(item) for item in items],
        "total" : total
    }


@user_role_router.get("/get/{user_id}", response_model=UserRoleResponse)
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            user: User = Depends(get_user_for_path)):
    
    check_admin(db, current_user, Permission.club_owner)
    user_role = get_user_role_or_404(user.id, db)
    return user_role
