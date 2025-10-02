from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession


from src.userauth.dependencies import RoleChecker
from src.items.schemas import Items
from src.db.main import get_session
from .schemas import TagAddModel, TagCreateModel, TagModel
from .services import TagService
from src.logging import logger

tags_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@tags_router.get("/", response_model=List[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session: AsyncSession = Depends(get_session)):

    logger.info("Getting all tags: processing request..")
    tags = await tag_service.get_tags(session)
    logger.info("Getting all tags: returning result..")

    return tags


@tags_router.post("/", response_model=TagModel, status_code=status.HTTP_201_CREATED, dependencies=[user_role_checker])
async def add_tag(tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:

    logger.info("Adding tag: processing request..")
    tag_added = await tag_service.add_tag(tag_data, session)
    logger.info("Adding tag: returning result..")

    return tag_added


@tags_router.post("/item/{item_uid}/tags", response_model=Items, dependencies=[user_role_checker])
async def add_tags_to_item(item_uid: str, tag_data: TagAddModel, session: AsyncSession = Depends(get_session)) -> Items:

    logger.info(f"Adding tags to item {item_uid}: processing request..")
    item_with_tag = await tag_service.add_tags_to_item(item_uid, tag_data, session
    )
    logger.info("Adding tags to item: returning result..")


    return item_with_tag


@tags_router.put("/{tag_uid}", response_model=TagModel, dependencies=[user_role_checker])
async def update_tag(tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:
    
    logger.info(f"Updating tag {tag_uid}: processing request..")
    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)
    logger.info("Updating tag: returning result..")

    return updated_tag


@tags_router.delete("/{tag_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[user_role_checker])
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)) -> None:
    
    logger.info(f"Deleting tag {tag_uid}: processing request..")
    deleted_tag = await tag_service.delete_tag(tag_uid, session)
    if deleted_tag:
        logger.info("Deleting tag: delete tag success..")
        return deleted_tag
    logger.error("Deleting tag: tag not found")