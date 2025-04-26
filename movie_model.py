
from beanie import Document
from pydantic import BaseModel

class MovieRequest(BaseModel):
    title: str
    comment: str

class Movie(Document):
    title: str
    comment: str

    class Settings:
        name = "movies"

#class User(Document):
  #  email: EmailStr
  #  hashed_password: str
    
   # class Settings:
      #  name = "users"  # This will store users in the "users" collection


class Review(Document):
    id: int
    rating: int
    review: str = ""  # Added review field with default empty string

    class Settings:
        name = "reviews"

class ReviewRequest(BaseModel):
    rating: int
    review: str = ""

class Watchlist(Document):
    id: int
    watched: bool = False

    class Settings:
        name = "watchlist"


class WatchlistRequest(BaseModel):
    watched: bool
