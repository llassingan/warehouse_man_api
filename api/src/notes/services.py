from fastapi import HTTPException, status
from sqlmodel import desc, select

from src.db.models import Notes
from src.notes.schemas import CreateNote
from src.userauth.services import UserService
from app.src.items.services import ItemsService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors import (
    ItemNotFound,
    UserNotFound
)


item_service = ItemsService()
user_service = UserService()


class NotesService:
    async def add_note(self, user_email:str, item_uid:str, note_data:CreateNote, session:AsyncSession):
        
        try:
            item = await item_service.get_item(item_uid, session)
            if not item:
                raise ItemNotFound()
            user = await user_service.get_user_by_email(user_email, session)
            if not user:
                raise UserNotFound()
            new_note = Notes(
                **note_data.model_dump()
            )
            new_note.user = user
            new_note.item = item
            session.add(new_note)
            await session.commit()
            await session.refresh(new_note)
            return new_note
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="something went wrong"
            )
        

    async def get_note(self, note_uid: str, session: AsyncSession):

        statement = select(Notes).where(Notes.uid == note_uid)
        result = await session.exec(statement)
        return result.first()
    

    async def get_all_notes(self, session: AsyncSession):
        statement = select(Notes).order_by(desc(Notes.created_at))
        result = await session.exec(statement)
        return result.all()
    

    async def delete_note_from_item(self, note_uid: str, user_email: str, session: AsyncSession):

        user = await user_service.get_user_by_email(user_email, session)
        note = await self.get_note(note_uid, session)
        
        if not note or (note.user is not user):
            raise HTTPException(
                detail="Cannot delete this note",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        
        await session.delete(note)
        await session.commit()
        return note