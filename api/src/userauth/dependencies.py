from fastapi.security import HTTPBearer
from fastapi import Request, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from .utils import decode_token
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from .services import UserService
from src.db.models import User
from src.errors import(
    InvalidToken,
    RevokedToken,
    AccessTokenRequired,
    RefreshTokenRequired,
    InsufficientPermission,
    InvalidCredentials,
    AccountNotVerified
)


user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)
    
    def token_valid(self, token: str) -> bool:
        return decode_token(token) is not None
    
    async def __call__(self, request:Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)
        if not token_data: 
            raise InvalidToken
        if not self.token_valid(token):
            raise InvalidToken()
        if await token_in_blocklist(token_data['jti']):
            raise RevokedToken()
        self.verify_token_data(token_data)
        return token_data 

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")
    
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data['refresh']:
            raise AccessTokenRequired()

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) -> None:
        if not token_data['refresh']:
            raise RefreshTokenRequired()

async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), 
                     session: AsyncSession = Depends(get_session)):
    user_email= token_details['user']['email']
    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise InvalidCredentials()
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not current_user.is_verified:
            raise AccountNotVerified()
        
        if current_user.role not in self.allowed_roles:
            raise InsufficientPermission()
        return True

