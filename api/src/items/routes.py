from fastapi import APIRouter, status, Depends
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import Items, ItemDetails,ItemUpdate,CreateItems
from ..db.main import get_session
from .services import ItemsService
from src.userauth.dependencies import AccessTokenBearer
from src.userauth.dependencies import RoleChecker
from src.errors import (
    ItemNotFound
)

# "/items"
item_router = APIRouter()

item_service = ItemsService()

role_checker= Depends(RoleChecker(['admin','user']))

access_token_bearer = AccessTokenBearer()


@item_router.get("/",response_model=List[Items]
                 , dependencies= [role_checker]
                 )
async def get_all_items(session:AsyncSession = Depends(get_session),
                        _: dict=Depends(access_token_bearer)):

    items = await item_service.get_all_items(session)
    
    return items


@item_router.get("/user/{user_uid}",response_model=List[Items]
                 , dependencies= [role_checker] 
                 )
async def get_user_item_submission(
                        user_uid :str,
                        session:AsyncSession = Depends(get_session),
                        _: dict=Depends(access_token_bearer)):
    items = await item_service.get_user_items(user_uid,session)

    return items



@item_router.post("/", response_model=Items, status_code=status.HTTP_201_CREATED, dependencies= [role_checker])
async def create_item(item_data:CreateItems , session:AsyncSession = Depends(get_session),
                        token_details: dict=Depends(access_token_bearer) ):
    
    user_uid = token_details['user']['user_uid']
    new_item = await item_service.create_item(item_data, user_uid,session)
    
    return new_item


@item_router.get("/{item_uid}", response_model=ItemDetails, status_code=status.HTTP_200_OK, dependencies= [role_checker])
async def get_item(item_uid: str, session:AsyncSession = Depends(get_session),
                        _: dict=Depends(access_token_bearer) ):
    
    item = await item_service.get_item(item_uid, session)
    
    if item:
        return item
    raise ItemNotFound()


@item_router.patch("/{item_uid}", response_model=Items, status_code=status.HTTP_200_OK, dependencies= [role_checker])
async def update_item(item_uid: str, item_latest: ItemUpdate, session:AsyncSession = Depends(get_session),
                        _: dict=Depends(access_token_bearer) ):
    
    updated_item = await item_service.update_item(item_uid, item_latest, session)
    
    if updated_item:
        return updated_item
    raise ItemNotFound()


@item_router.delete("/{item_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies= [role_checker])
async def delete_item(item_uid: str, session:AsyncSession = Depends(get_session),
                        _: dict=Depends(access_token_bearer) ):
    
    deleted_item = await item_service.delete_item(item_uid, session)

    if deleted_item:
        return
    
    raise ItemNotFound()