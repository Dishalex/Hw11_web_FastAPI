from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional

from src.schemas.user import UserResponse


class ContactModel(BaseModel):
    first_name: str = Field(max_lenght=25)
    last_name: str = Field(max_lenght=25)
    email: str = EmailStr
    phone_number: str = Field(max_lenght=25)
    birth_date: date | None = None
    additional_data: str = Field()
    

class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: str = EmailStr
    phone_number: str
    birth_date: Optional[date]
    additional_data: str 
    created_at: datetime
    updated_at: datetime
    user: UserResponse | None

    
    class Config:
        from_attributes = True