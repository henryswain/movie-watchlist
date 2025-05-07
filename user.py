from typing import Annotated
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from jwt_auth import (
    LoginResult,
    Token,
    TokenData,
    create_access_token,
    decode_jwt_token,
)
from user_model import User, UserDto, UserRequest, ensure_admin_role

pwd_context = CryptContext(schemes=["bcrypt"])


class HashPassword:
    def create_hash(self, password: str):
        return pwd_context.hash(password)

    def verify_hash(self, input_password: str, hashed_password: str):
        return pwd_context.verify(input_password, hashed_password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/sign-in")

hash_password = HashPassword()


def get_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    print(token)
    return decode_jwt_token(token)


user_router = APIRouter()


@user_router.post("/sign-in")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> LoginResult:  # Change return type to LoginResult
    ## Authenticate user by verifying the user in DB
    username = form_data.username
    existing_user = await User.find_one(User.username == username)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    authenticated = hash_password.verify_hash(
        form_data.password, existing_user.password
    )
    if authenticated:
        access_token = create_access_token(
            {"username": username, "role": existing_user.role}
        )
        # Return role information with the token
        return LoginResult(
            access_token=access_token, username=username, role=existing_user.role
        )

    raise HTTPException(status_code=401, detail="Invalid username or password")


@user_router.post("/sign-in")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    ## Authenticate user by verifying the user in DB
    username = form_data.username
    existing_user = await User.find_one(User.username == username)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    authenticated = hash_password.verify_hash(
        form_data.password, existing_user.password
    )
    if authenticated:
        access_token = create_access_token(
            {"username": username, "role": existing_user.role}
        )
        return Token(access_token=access_token)

    raise HTTPException(status_code=401, detail="Invalid username or password")


@user_router.get("")
async def get_all_users(user: Annotated[TokenData, Depends(get_user)]) -> list[UserDto]:
    ensure_admin_role(user)
    users = await User.find_all().to_list()
    result = []
    for u in users:
        result.append(
            UserDto(id=str(u.id), username=u.username, email=u.email, role=u.role)
        )
    return result


@user_router.post("/{id}")
async def update_user_role(
    id: PydanticObjectId, user: Annotated[TokenData, Depends(get_user)]
) -> dict:
    ensure_admin_role(user)
    affected_user = await User.get(id)
    if not affected_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user with ID={id} is not found.",
        )

    if affected_user.role == "BasicUser":
        affected_user.role = "AdminUser"
    else:
        affected_user.role = "BasicUser"
    await affected_user.save()
    return {"newRole": affected_user.role}
