from passlib.context import CryptContext
from datetime import timedelta,datetime
import jwt
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

from src.config import Config 

passwd_context = CryptContext(
    schemes=["bcrypt"]
    ,deprecated="auto"
)

ACCESS_TOKEN_EXPIRY = 3600

def generate_pwhash(password:str) -> str:

    hashed_pass = passwd_context.hash(password)
    return hashed_pass


def verified_pwd(password:str, hash:str) -> bool:
    
    return passwd_context.verify(password,hash)


def create_access_token (user_data: dict, expiry:timedelta=None, refresh: bool = False):
    
    payload ={}
    payload["user"] = user_data 
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token:str) -> dict:
    
    try: 
        token_data= jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET_KEY,
            algorithms=Config.JWT_ALGORITHM
        )
        
        return token_data
    
    except jwt.PyJWTError as e:
        logging.exception(e)
        
        return None 


serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET_KEY, salt="email-configuration"
)


def create_url_safe_token(data: dict):
    """Serialize a dict into a URLSafe token"""

    token = serializer.dumps(data)

    return token

def decode_url_safe_token(token:str):
    """Deserialize a URLSafe token to get data"""
    
    try:
        token_data = serializer.loads(token)

        return token_data

    except Exception as e:
        logging.error(str(e))
