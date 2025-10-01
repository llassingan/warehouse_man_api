from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional



class Notes(BaseModel):
    uid: uuid.UUID
    note_text: str
    user_uid: Optional[uuid.UUID] 
    book_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime 

class CreateNote(BaseModel):
    review_text: str