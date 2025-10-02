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
from src.logging import logger

# "/items"
item_router = APIRouter()

item_service = ItemsService()

admin_role_checker= Depends(RoleChecker(['admin']))
user_role_checker= Depends(RoleChecker(['admin','user']))

access_token_bearer = AccessTokenBearer()


@item_router.get("/",response_model=List[Items], dependencies= [user_role_checker])
async def get_all_items(session:AsyncSession = Depends(get_session), _: dict=Depends(access_token_bearer)):

    logger.info("Getting all items: processing request..")
    items = await item_service.get_all_items(session)
    logger.info("Getting all items: returning result..")
    
    return items


@item_router.get("/user/{user_uid}",response_model=List[Items], dependencies= [user_role_checker])
async def get_user_item_submission(user_uid :str, session:AsyncSession = Depends(get_session), _: dict=Depends(access_token_bearer)):
    
    logger.info("Getting user item submission: processing request..")
    items = await item_service.get_user_items(user_uid,session)
    logger.info("Getting user item submission: returning result..")
    
    return items



@item_router.post("/", response_model=Items, status_code=status.HTTP_201_CREATED, dependencies= [user_role_checker])
async def create_item(item_data:CreateItems , session:AsyncSession = Depends(get_session), token_details: dict=Depends(access_token_bearer) ):
    
    logger.info(f"Creating item by {token_details['user']['user_uid']} : processing request..")
    user_uid = token_details['user']['user_uid']
    new_item = await item_service.create_item(item_data, user_uid,session)
    logger.info("Creating item: returning result..")
    
    return new_item


@item_router.get("/{item_uid}", response_model=ItemDetails, status_code=status.HTTP_200_OK, dependencies= [user_role_checker])
async def get_item(item_uid: str, session:AsyncSession = Depends(get_session), _: dict=Depends(access_token_bearer) ):
    
    logger.info("Getting item: processing request..")
    item = await item_service.get_item(item_uid, session)
    if item:
        logger.info("Getting user item submission: returning result..")
        return item
    logger.error("Getting item: item not found")
    raise ItemNotFound()


@item_router.patch("/{item_uid}", response_model=Items, status_code=status.HTTP_200_OK, dependencies= [user_role_checker])
async def update_item(item_uid: str, item_latest: ItemUpdate, session:AsyncSession = Depends(get_session), _: dict=Depends(access_token_bearer) ):
    

    logger.info("Updating item: processing request..")
    updated_item = await item_service.update_item(item_uid, item_latest, session)
    
    if updated_item:
        logger.info("Updating item: returning result..")
        return updated_item
    logger.error("Updating item: item not found")
    raise ItemNotFound()


@item_router.delete("/{item_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies= [admin_role_checker])
async def delete_item(item_uid: str, session:AsyncSession = Depends(get_session), _: dict=Depends(access_token_bearer) ):
    
    logger.info("Deleting item: processing request..")
    deleted_item = await item_service.delete_item(item_uid, session)

    if deleted_item:
        logger.info("Deleting item: delete item success..")
        return
    logger.error("Deleting item: item not found")
    raise ItemNotFound()