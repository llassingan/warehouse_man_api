from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.items.services import ItemsService
from src.db.models import Tag
from .schemas import TagAddModel, TagCreateModel
from src.errors import (
    TagNotFound,
    TagAlreadyExists,
    ItemNotFound
)
from src.logging import logger


item_service = ItemsService()



class TagService:

    async def get_tags(self, session: AsyncSession):

        try:
            logger.info("Getting all tags: getting data from databases..")
            statement = select(Tag).order_by(desc(Tag.created_at))
            result = await session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise
    

    async def add_tags_to_item(self, item_uid: str, tag_data: TagAddModel, session: AsyncSession):

        try:
            logger.info(f"Adding tags to item: inserting to database..")    
            item = await item_service.get_item(item_uid, session=session)
            if not item:
                logger.error("Adding tags to item: item not found")
                raise ItemNotFound()

            for tag_item in tag_data.tags:
                result = await session.exec(
                    select(Tag).where(Tag.name == tag_item.name)
                )

                tag = result.one_or_none()
                if not tag:
                    tag = Tag(name=tag_item.name)

                item.tags.append(tag)
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item
        
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise


    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):

        try:
            logger.info(f"Getting tag by uid: getting data from database..")
            statement = select(Tag).where(Tag.uid == tag_uid)

            result = await session.exec(statement)

            return result.first()
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise



    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        
        try:
            logger.info("Adding tag: inserting to database..")
            statement = select(Tag).where(Tag.name == tag_data.name)
            result = await session.exec(statement)
            tag = result.first()

            if tag:
                logger.error("Adding tag: tag already exists")
                raise TagAlreadyExists()
            
            new_tag = Tag(name=tag_data.name)

            session.add(new_tag)
            await session.commit()

            return new_tag
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise




    async def update_tag(self, tag_uid, tag_update_data: TagCreateModel, session: AsyncSession):
        
        try:
            logger.info(f"Updating tag: updating data in database..")
            tag = await self.get_tag_by_uid(tag_uid, session)

            update_data_dict = tag_update_data.model_dump()
            for k, v in update_data_dict.items():
                setattr(tag, k, v)

                await session.commit()
                await session.refresh(tag)

            return tag
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise


    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        
        try:
            logger.info(f"Deleting tag: deleting data from database..")
            tag = await self.get_tag_by_uid(tag_uid,session)
            if not tag:
                logger.error("Deleting tag: tag not found")
                raise TagNotFound()

            await session.delete(tag)
            await session.commit()

            return tag
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise