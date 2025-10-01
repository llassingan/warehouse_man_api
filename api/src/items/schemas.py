from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime,date
from typing import List

from src.notes.schemas import Review
from src.tags.schemas import TagModel



class Items(BaseModel):
    uid: uuid.UUID
    title: str
    owner: str
    stored_exp_date: date
    ph_number: str
    created_at: datetime
    updated_at: datetime

class ItemDetails(Items):
    notes:List[Review]
    tags:List[TagModel]



class ItemUpdate(BaseModel):
    title: str
    owner: str
    ph_number: str

class CreateItems(BaseModel):
    title: str
    owner: str
    stored_exp_date: date
    ph_number: str