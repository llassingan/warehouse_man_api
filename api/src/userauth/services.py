from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.db.models import User
from .schemas import CreateUser
from .utils import generate_pwhash
from src.logging import logger


class UserService:
    async def get_user_by_email(self, email:str, session: AsyncSession):
        
        try:
            logger.info(f"Getting user by email: Getting data from database..")
            query = select(User).where(User.email == email)
            user_getter = await session.exec(query)
            
            return user_getter.first()
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise 
    

    async def user_exist(self,email:str,session:AsyncSession ):

        try:
            logger.info(f"Checking if user exists: Getting data from database..")
            user = await self.get_user_by_email(email,session)
            return True if user else False
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise
    

    async def create_user(self, user_data:CreateUser, session):
        
        try:
            logger.info(f"Creating user: Creating user in database..")
            user_data_dict = user_data.model_dump()
            new_user = User(
                **user_data_dict
            )
            new_user.password_hash = generate_pwhash(user_data_dict["password"])
            new_user.role = "user"
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return new_user
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise
    

    async def update_user_verified(self, user: User, user_Data: dict, session):
        
        try:
            logger.info(f"Updating user: Updating user in database..")
            for key, value in user_Data.items():
                setattr(user, key, value)
            
            await session.commit()
            await session.refresh(user)

            return user
        except Exception as e:
            logger.error(f"DB Error: {e}")
            raise
        
        



