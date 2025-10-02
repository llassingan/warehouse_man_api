from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from datetime import datetime

from .schemas import CreateItems, Items, ItemUpdate
from src.db.models import Items
from src.logging import logger


class ItemsService:
    async def get_all_items(self, session:AsyncSession):

        try:
            logger.info("Getting all items: getting data from databases..")
            query = select(Items).order_by(desc(Items.created_at))
            results = await session.exec(query)
            return results.all()
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise e
    

    async def get_user_items(self, user_uid:str, session:AsyncSession):
        
        try:
            logger.info("Getting user item submission: getting data from databases..")
            query = select(Items).where(Items.user_uid == user_uid).order_by(desc(Items.created_at))
            results = await session.exec(query)
            return results.all()
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise e
    

    async def get_item(self, item_uid:str, session:AsyncSession):
        
        try:
            logger.info("Getting item: getting data from databases..")
            query = select(Items).where(Items.uid == item_uid)
            result = await session.exec(query)
            return result.first() if result is not None else None
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise e


    async def create_item(self, item_data:CreateItems, user_uid:str,session:AsyncSession):

        try:
            logger.info("Creating item: inserting item to database..")
            item_data_dict = item_data.model_dump()
            new_item = Items(
                **item_data_dict
            )
            new_item.stored_exp_date = datetime.strptime(item_data_dict["stored_exp_date"],"%Y-%m-%d")
            new_item.user_uid = user_uid
            
            session.add(new_item)
            await session.commit()
            await session.refresh(new_item)
            return new_item
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise e


    async def update_item(self, item_uid:str, update_data:ItemUpdate, session:AsyncSession):
        
        try:
            updated_item = await self.get_item(item_uid, session)
            if updated_item is not None:
                updated_item_dict = update_data.model_dump()

                for k,v in updated_item_dict.items():
                    setattr(updated_item,k,v)

                await session.commit()
                return updated_item
            
            return None
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise e


    async def delete_item(self, item_uid:str, session:AsyncSession):
        
        try:
            deleted_item = await self.get_item(item_uid, session)

            if deleted_item is not None:
                await session.delete(deleted_item)
                await session.commit()
                return deleted_item

            return None
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise e