from pydantic import BaseModel, ConfigDict



class CreateUserRole(BaseModel):
    role_id: int
    user_id: int


class UpdateUserRole(BaseModel):
    role_id: int | None = None


class UserRoleResponse(BaseModel):
    role_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)