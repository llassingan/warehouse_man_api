from fastapi import (
    APIRouter, 
    Depends, 
    status, 
    HTTPException
)
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse

from .schemas import (
    CreateUser, 
    UserModel,
    UserLogin, 
    UserItems,
    EmailModel,
    PasswordResetRequest,
    PasswordResetConfirm
)
from .services import UserService
from src.db.main import get_session
from .utils import (
    create_access_token, 
    verified_pwd, 
    generate_pwhash,
    create_url_safe_token,
    decode_url_safe_token
)

from .dependencies import (
    RefreshTokenBearer, 
    AccessTokenBearer, 
    get_current_user, 
    RoleChecker
)
from src.db.redis import add_jti_to_blocklist
from src.errors import (
    UserAlreadyExists,
    InvalidCredentials,
    InvalidToken,
    UserNotFound
)
from src.config import Config
from src.celery_task import send_email



auth_router = APIRouter()
user_service = UserService()
role_checker= RoleChecker(['admin','user'])

REFRESH_TOKEN_EXPIRY = 2
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):

    emails = emails.addresses
    html = "<h1>Welcome to the Warehouse App</h1>"
    subject = "Welcome to the Warehouse App"

    send_email.delay(
        recipients=emails,
        subject=subject,
        html_message=html
    )

    return {"message": "Email sent successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: CreateUser, session:AsyncSession = Depends(get_session) ):
    
    email  =user_data.email
    is_exist = await user_service.user_exist(email, session)
    if is_exist: 
        raise UserAlreadyExists()
    
    user_create = await user_service.create_user(user_data,session)
    
    token_data = create_url_safe_token({"email":email})
    
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token_data}"
    html_message = f"""
    <h1>Verify your email</h1>
    <p> Please click this <a href="{link}">link</a> to verify your email</p>

    """
    
    subject="Warehouse App email verification"
    send_email.delay(
        recipients=[email],
        subject=subject,
        html_message=html_message
    )
    
    return  {
        "messages": "Account Created Successfully!. Check email for verification",
        "user": user_create
    }


@auth_router.get("/verify/{token}")
async def verify_email(token:str, session: AsyncSession = Depends(get_session)):
    
    token_data = decode_url_safe_token(token)
    
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        await user_service.update_user_verified(user, {"is_verified":True}, session)
        return JSONResponse(content={
            "message": "Account verified successfully"},
            status_code=status.HTTP_200_OK)
    
    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_400_BAD_REQUEST
    )


@auth_router.post("/login")
async def login_user(logindata:UserLogin, session: AsyncSession = Depends(get_session)):
    
    email = logindata.email
    password = logindata.password
    user = await user_service.get_user_by_email(email, session)
    if not user: 
        raise InvalidCredentials()
    
    is_pwd_valid = verified_pwd(password, user.password_hash)
    if is_pwd_valid:
        access_token = create_access_token(
            user_data= {
                "email":user.email,
                "user_uid": str(user.uid),
                "role": user.role
            }
        )
        refresh_token = create_access_token(
            user_data={
                "email":user.email,
                "user_uid": str(user.uid)   
            },
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
        )
        return JSONResponse(
            content={
                "message":"Login Successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user":{
                    "email": user.email,
                    "uid": str(user.uid),
                    "role": user.role
                }
            }
        )
    raise InvalidCredentials()
    

@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data = token_details['user']
        )

        return JSONResponse(content={
            "access_token": new_access_token
        })
    
    raise InvalidToken()


@auth_router.get("/me", response_model=UserItems)
async def get_current_user(user: UserModel = Depends(get_current_user), _:bool = Depends(role_checker)):

    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(access_token_bearer)):

    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    
    return JSONResponse(content={"message": "Successfully logged out"}, 
        status_code=status.HTTP_200_OK)


@auth_router.post("/password_reset_request")
async def password_reset_request(email_data: PasswordResetRequest):
    
    email = email_data.email
    
    token_data = create_url_safe_token({"email":email})
    
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token_data}"
    html_message = f"""
    <h1>Reset your password</h1>
    <p> Please click this <a href="{link}">link</a> to reset your password</p>

    """
    
    subject="Warehouse password reset"
    send_email.delay(
        recipients=[email],
        subject=subject,
        html_message=html_message
    )

    return  JSONResponse(content={
        "messages": "Please check your email for instruction to reset your password"},
        status_code=status.HTTP_200_OK)

# Simplied Version (No FE) 
@auth_router.post("/password-reset-confirm/{token}")
async def password_reset_confirm(token:str, password_data:PasswordResetConfirm,session: AsyncSession = Depends(get_session)):
    
    if password_data.confirm_password != password_data.new_password:
        raise HTTPException(
            detail="Password don't match",
            status_code=status.HTTP_400_BAD_REQUEST)
    
    token_data = decode_url_safe_token(token)
    
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        
        await user_service.update_user_verified(user, {"password_hash":generate_pwhash(password_data.new_password)}, session)
        
        return JSONResponse(content={
            "message": "Password updated successfully"},
            status_code=status.HTTP_200_OK)
    
    return JSONResponse(
        content={
            "message": "Error occured during reset password"
        },
        status_code=status.HTTP_400_BAD_REQUEST
    )