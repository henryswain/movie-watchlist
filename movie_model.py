from typing import Optional, List
from datetime import datetime
from beanie import Document
from pydantic import BaseModel, Field

# Request Models (for API input)
class MovieRequest(BaseModel):
    title: str
    comment: str = ""
    rating: int = 0
    review: str = ""  # Add review field for input
    watched: bool = False

class ReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)  # Rating between 1-5
    review: str = ""  # Review explaining the rating

class WatchlistRequest(BaseModel):
    movie_id: str
    watched: bool = False
    favorite: bool = False

# MongoDB Document Models
class Movie(Document):
    title: str
    comment: str = ""
    review: str = ""  # Store review for each movie
    added_by: str = "anonymous"  # Username of who added the movie
    date_added: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "movies"  # Collection name

class Review(Document):
    movie_id: str  # Reference to Movie.id
    user_id: str  # Reference to User.id (this links the review to a user)
    rating: int = Field(..., ge=1, le=5)  # Rating between 1-5
    review: str = ""  # Review explaining the rating
    date_added: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "reviews"  # Collection name

class Watchlist(Document):
    movie_id: str  # Reference to Movie.id
    user_id: str  # Reference to User.id (this links the movie to the user’s watchlist)
    watched: bool = False
    favorite: bool = False
    date_added: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "watchlist"  # Collection name

# Response Models (for API output)
class MovieResponse(BaseModel):
    id: str
    title: str
    comment: str
    review: Optional[str] = None  # Make review optional for response
    added_by: str
    date_added: datetime
    avg_rating: Optional[float] = None
    user_review: Optional[dict] = None
    watchlist_status: Optional[dict] = None
    is_admin: bool = False

# New: Response models for reviews and watchlist
class ReviewResponse(BaseModel):
    id: str
    movie_id: str
    user_id: str
    rating: int
    review: str
    date_added: datetime
    movie_title: Optional[str] = None

class WatchlistResponse(BaseModel):
    id: str
    movie_id: str
    user_id: str
    watched: bool
    favorite: bool
    date_added: datetime
    movie_title: Optional[str] = None
