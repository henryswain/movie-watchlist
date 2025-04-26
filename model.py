
from pydantic import BaseModel

class MovieRequest(BaseModel):
    title: str
    comment: str
    rating: int
    review: str = ""  # Added review field with default empty string
    watched: bool = False


class Movie(BaseModel):
    id: int
    title: str
    comment: str
    rating: int
    review: str = ""  # Added review field with default empty string
    watched: bool = False

#class User(Document):
  #  email: EmailStr
  #  hashed_password: str
    
   # class Settings:
      #  name = "users"  # This will store users in the "users" collection
