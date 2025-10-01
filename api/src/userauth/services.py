from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.db.models import User
from .schemas import CreateUser
from .utils import generate_pwhash


class UserService:
    async def get_user_by_email(self, email:str, session: AsyncSession):
        
        query = select(User).where(User.email == email)
        user_getter = await session.exec(query)
        
        return user_getter.first()
    

    async def user_exist(self,email:str,session:AsyncSession ):

        user = await self.get_user_by_email(email,session)
        return True if user else False
    

    async def create_user(self, user_data:CreateUser, session):
        
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
    

    async def update_user_verified(self, user: User, user_Data: dict, session):
        
        for key, value in user_Data.items():
            setattr(user, key, value)
        
        await session.commit()
        await session.refresh(user)

        return user
        
        



