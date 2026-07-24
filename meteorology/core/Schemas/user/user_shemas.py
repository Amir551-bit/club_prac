from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime


class UserRegister(BaseModel):  
    user_name: str 
    first_name: str
    last_name: str
    number_phone: str

    @field_validator("number_phone")
    @classmethod
    def validate_number_phone(cls, value: str) -> str:
        # ۱. حذف فاصله‌های خالی احتمالی از ابتدا و انتها
        phone = value.strip()
                  # [شروع : پایان]
        if phone.startswith("+98"):
            phone = phone[3:]           # خود ایندکس 3 پاک نمیشه 
        elif phone.startswith("0098"):
            phone = phone[4:]
        elif phone.startswith("0"):          
            phone = phone[1:]
            
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("شماره تلفن وارد شده معتبر نیست. باید شامل ۱۰ رقم بدون صفر اول باشد (مثال: 9123456789)")
            
        return phone


class UserLogin(BaseModel):
    user_name: str
    number_phone: str


class UserResponseModel(BaseModel):
    id: int
    user_name: str
    first_name: str
    last_name: str
    number_phone: str
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)