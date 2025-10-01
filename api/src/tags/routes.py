from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession


from src.userauth.dependencies import RoleChecker
from src.items.schemas import Items
from src.db.main import get_session

from .schemas import TagAddModel, TagCreateModel, TagModel
from .services import TagService

tags_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@tags_router.get("/", response_model=List[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session: AsyncSession = Depends(get_session)):

    tags = await tag_service.get_tags(session)

    return tags


@tags_router.post("/", response_model=TagModel, status_code=status.HTTP_201_CREATED, dependencies=[user_role_checker])
async def add_tag(tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:

    tag_added = await tag_service.add_tag(tag_data, session)

    return tag_added


@tags_router.post("/item/{item_uid}/tags", response_model=Items, dependencies=[user_role_checker])
async def add_tags_to_item(item_uid: str, tag_data: TagAddModel, session: AsyncSession = Depends(get_session)) -> Items:

    item_with_tag = await tag_service.add_tags_to_item(item_uid, tag_data, session
    )

    return item_with_tag


@tags_router.put("/{tag_uid}", response_model=TagModel, dependencies=[user_role_checker])
async def update_tag(tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:
    
    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)

    return updated_tag


@tags_router.delete("/{tag_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[user_role_checker])
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)) -> None:
    
    deleted_tag = await tag_service.delete_tag(tag_uid, session)
    if deleted_tag:
        return deleted_tag