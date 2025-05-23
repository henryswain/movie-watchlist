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
from user_model import TokenValidationResponse, User, UserDto, UserRequest, ensure_admin_role
from logging_config import setup_logger

logger = setup_logger()

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
        logger.error(f"Failed login attempt for username '{username}: User not found")
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
        logger.info(f"User '{username}' successfully signed in. Role: {existing_user.role}")
        return LoginResult(
            access_token=access_token, username=username, role=existing_user.role
        )

    logger.error(f"Failed login attempt for username '{username}': Invalid password")
    raise HTTPException(status_code=401, detail="Invalid username or password")


@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_user(user_request: UserRequest) -> dict:
    """Register a new user"""
    # Check if username already exists
    existing_user = await User.find_one(User.username == user_request.username)
    if existing_user:
        logger.warning(f"User signup failed: Username '{user_request.username}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # Check if email already exists
    existing_email = await User.find_one(User.email == user_request.email)
    if existing_email:
        logger.warning(f"User signup failed: Email '{user_request.email}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    # Hash the password
    hashed_password = hash_password.create_hash(user_request.password)

    # Create new user
    new_user = User(
        username=user_request.username,
        email=user_request.email,
        password=hashed_password,
        role="BasicUser",  # Default role for new users
    )

    await new_user.insert()
    logger.info(f"New user '{user_request.username}' signed up successfully. Role: BasicUser")

    return {"message": "User created successfully"}



@user_router.get("/validate-token", response_model=TokenValidationResponse)
async def validate_token(token_data: Annotated[TokenData, Depends(get_user)]) -> TokenValidationResponse:
    logger.info(f"Token validated for user '{token_data.username}'. Role: {token_data.role}")
    return TokenValidationResponse(
        username=token_data.username,
        role=token_data.role,
        valid=True
    )

@user_router.post("/logout")
async def logout_user(token_data: Annotated[TokenData, Depends(get_user)]) -> dict:
    logger.info(f"User: '{token_data.username}' logged out. Role: {token_data.role}")
    return {"message": "Logged out successfully"}


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
