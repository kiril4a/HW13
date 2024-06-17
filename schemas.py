from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class ContactInDB(ContactBase):
    id: int

    class Config:
        orm_mode = True

class AvatarUploadRequest(BaseModel):
    api_key: str
