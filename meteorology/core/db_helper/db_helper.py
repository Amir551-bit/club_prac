from fastapi import Depends
from sqlite.database import get_db, Sessionlocal
from core.Models.role.role_model import Role
from core.Models.user.user_model import User
from core.Models.user_role.user_role_model import UserRole
from core.Models.role.permission import (ALL_PERMISSION, ATHLETE, CLUB_OWNER, CLUB_MANAGER, COACH, GENERAL_VISITOR)
from sqlalchemy.orm import Session
from core.execptions.execption import raise_not_found



def seeds_role():
    roles_to_add = []

    role_list = [
        {"name" : "super admin", "permission" : ALL_PERMISSION},
        {"name" : "club owner", "permission" : CLUB_OWNER},
        {"name" : "club manager", "permission" : CLUB_MANAGER},
        {"name" : "coach", "permission" : COACH},
        {"name" : "athlete", "permission" : ATHLETE},
        {"name" : "general_visitor", "permission" : GENERAL_VISITOR}
    ]

    with Sessionlocal() as db:
        for role in role_list:
            exists = db.query(Role).filter(Role.name==role["name"]).first()
            if not exists:
                new_role = Role(name=role["name"], permission=role["permission"])
                roles_to_add.append(new_role)
        if roles_to_add:
            db.add_all(roles_to_add)
            db.commit()
            print("Roles seeded successfully!")



def create_admin():
    with Sessionlocal() as db:
        user_exists = db.query(User).filter(User.user_name=="amir123").first()
        if not user_exists:
            raise_not_found("user amir123 is not found")
        exists_role = db.query(Role).filter(Role.name=="super admin").first()
        if not exists_role:
            raise_not_found("role is not found")
        user_role = db.query(UserRole).filter(UserRole.user_id==user_exists.id).first()
        user_role.role_id = exists_role.id
        db.commit()
        db.refresh(user_role)
        print("amir123 is super admin successfully")