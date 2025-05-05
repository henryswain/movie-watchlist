from datetime import datetime, timedelta
from typing import Optional, Union, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from my_config import get_settings

# Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str
    role: str = "BasicUser"
    exp: Optional[datetime] = None

# New: LoginResult class for user authentication response
class LoginResult(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str = "BasicUser"

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/sign-in")

# Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    config = get_settings()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)  # Default 30 days
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm="HS256")
    return encoded_jwt

def decode_jwt_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    config = get_settings()
    
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=["HS256"])
        username: str = payload.get("sub") or payload.get("username")
        if username is None:
            raise credentials_exception
        
        # Get expiration time and role
        exp = payload.get("exp")
        role = payload.get("role", "BasicUser")
        
        token_data = TokenData(username=username, role=role)
        if exp:
            token_data.exp = datetime.fromtimestamp(exp)
            
            # Check if token is expired
            if datetime.utcnow() > token_data.exp:
                raise credentials_exception
                
    except jwt.JWTError:
        raise credentials_exception
    return token_data

# Add this function to be imported in movie.py
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    """
    Dependency to get the current authenticated user from the token
    """
    return decode_jwt_token(token)