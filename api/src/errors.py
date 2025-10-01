from typing import Any, Callable
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class WarehouseException(Exception):
    """This is the base class for all Warehouse API errors"""
    pass

class InvalidToken(WarehouseException):
    """User has provided an invalid or expired token"""
    pass

class RevokedToken(WarehouseException):
    """User has provided a token that has been revoked"""
    pass

class AccessTokenRequired(WarehouseException):
    """User has provided a refresh token when an access token is needed"""
    pass

class RefreshTokenRequired(WarehouseException):
    """User has provided an access token when a refresh token is needed"""
    pass

class UserAlreadyExists(WarehouseException):
    """User has provided an email for a user who exists during sign up."""
    pass

class InvalidCredentials(WarehouseException):
    """User has provided wrong email or password during log in."""
    pass

class InsufficientPermission(WarehouseException):
    """User does not have the necessary permissions to perform an action."""
    pass

class ItemNotFound(WarehouseException):
    """Item Not found"""
    pass

class TagNotFound(WarehouseException):
    """Tag Not found"""
    pass

class TagAlreadyExists(WarehouseException):
    """Tag already exists"""
    pass

class UserNotFound(WarehouseException):
    """User Not found"""
    pass

class AccountNotVerified (WarehouseException):
    """Account is not yet vierified"""
    pass


def create_exception_handler(
    status_code: int,
    initial_detail: Any
) -> Callable[[Request,Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: WarehouseException):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_error_handlers(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        ItemNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Item not found",
                "error_code": "item_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )
    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "Tag Not Found", "error_code": "tag_not_found"},
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Tag Already exists",
                "error_code": "tag_exists",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account Not Verified",
                "error_code": "account_not_verified",
                "resolution": "Please verify your account by check your email"
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )