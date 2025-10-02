from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User
from src.notes.schemas import CreateNote
from src.userauth.dependencies import get_current_user, RoleChecker
from src.db.main import get_session
from .services import NotesService
from src.logging import logger


notes_router = APIRouter()

notes_service = NotesService()

admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@notes_router.get("/", dependencies=[user_role_checker])
async def get_all_notes(session: AsyncSession = Depends(get_session)):

    logger.info("Getting all notes: processing request..")
    notes = await notes_service.get_all_notes(session)
    logger.info("Getting all notes: returning result..")

    return notes


@notes_router.get("/{note_uid}", dependencies=[user_role_checker])
async def get_note(note_uid: str, session: AsyncSession = Depends(get_session)):

    logger.info(f"Getting note {note_uid}: processing request..")
    rev = await notes_service.get_note(note_uid, session)
    if not rev:
        logger.error("Getting note: note not found")
        raise
    logger.info("Getting note: returning result..")
    return rev


@notes_router.post("/item/{item_uid}")
async def add_item_note(item_uid:str, note_data: CreateNote, current_user: User= Depends(get_current_user), session: AsyncSession = Depends(get_session)):

    logger.info(f"Adding note to item {item_uid}: processing request..")
    new_note = await notes_service.add_note(
        current_user.email,
        item_uid,
        note_data,
        session
    )
    logger.info("Adding note to item: returning result..")
    return new_note


@notes_router.delete("/{note_uid}", dependencies=[admin_role_checker], status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_uid: str, current_user: User = Depends(get_current_user),session: AsyncSession = Depends(get_session)):

    logger.info(f"Deleting note {note_uid}: processing request..")
    note = await notes_service.delete_note_from_item(
        note_uid=note_uid, user_email=current_user.email, session=session
    )
    logger.info("Deleting note: delete note success..")
    if note:
        logger.error("Deleting note: note not found")
        return None