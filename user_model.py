from typing import Optional
from beanie import Document
from fastapi import HTTPException, status
from pydantic import BaseModel

from jwt_auth import TokenData


class User(Document):
    username: str
    email: str
    password: str  # hash & salted password in the database
    role: str = "BasicUser"
    photo: Optional[str] = None 

    class Settings:
        name = "users"


class UserRequest(BaseModel):
    """
    # model for user sign up
    """

    username: str
    email: str
    password: str  # plain text from user input

class TokenValidationResponse(BaseModel):
    username: str
    role: str
    valid: bool

class UserDto(BaseModel):
    id: str
    username: str
    email: str
    role: str
    photo: Optional[str] = None 


def ensure_admin_role(user: TokenData | None):
    if not user or not user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Please login.",
        )
    if user.role != "AdminUser":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have enough permissions for this action.",
        )
    return True