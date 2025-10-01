from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List

from src.items.schemas import Items
from src.notes.schemas import Notes


class CreateUser(BaseModel):
    username: str = Field(
        max_length=10
    )
    email:str = Field(
        max_length=70
    )
    password:str = Field(
        min_length=6
    )
    first_name:str = Field(
        max_length=25
    )
    last_name:str = Field(
        max_length=25
    )


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    password_hash: str = Field(
        exclude=True
    )
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
class UserItems(UserModel):
    items:List[Items]
    notes:List[Notes]


class UserLogin(BaseModel):
    email: str
    password: str

class EmailModel(BaseModel):
    addresses : List[str]


class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    new_password: str
    confirm_password: str