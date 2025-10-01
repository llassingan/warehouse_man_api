from sqlmodel import SQLModel, Field, Column, Relationship
from typing import Optional, List
import uuid
from datetime import datetime, date
import sqlalchemy.dialects.postgresql as pg


# ================ USER PART =================================
class User(SQLModel, table=True):
    __tablename__ = 'users'
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    username: str
    password_hash: str = Field(
        exclude=True
    )
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(
            pg.VARCHAR, 
            nullable=False, 
            server_default="user"
        )
    )
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now
        )
    )
    items: List["Items"]  = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    notes: List["Notes"]  = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    
    def __repr__(self):
        return f"<User {self.username}>"
    

 #  ========================== TAGS PART ==================================
class ItemTag(SQLModel, table=True):
    item_id: uuid.UUID = Field(default=None, foreign_key="items.uid", primary_key=True)
    tag_id: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    items: List["Items"] = Relationship(
        link_model=ItemTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"

# ========================= ITEMS PART ====================================

class Items(SQLModel, table=True):
    __tablename__ = "items"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    title: str
    owner: str
    stored_exp_date: date
    ph_number: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid") 
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now()
    ))
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now()
    ))
    user: Optional[User]  = Relationship(back_populates="items")
    notes: List["Notes"]  = Relationship(back_populates="item", sa_relationship_kwargs={"lazy": "selectin"})
    tags: List[Tag] = Relationship(
        link_model=ItemTag,
        back_populates="items",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    
    
    def __repr__(self):
        return f"<Item: {self.title}>"


# =========================== NOTES PART =============================

class Notes(SQLModel, table=True):
    __tablename__ = "notes"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    note_text: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    item_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="items.uid")
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now()
    ))
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now()
    ))
    user: Optional[User]  = Relationship(back_populates="notes")
    item: Optional[Items]  = Relationship(back_populates="notes")

    
    def __repr__(self):
        return f"<Notes for {self.item_uid} by user {self.user_uid}>"
    


   