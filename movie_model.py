from typing import Optional, List
from datetime import datetime
from beanie import Document
from pydantic import BaseModel, Field

# Request Models (for API input)
class MovieRequest(BaseModel):
    title: str
    comment: str = ""

class ReviewRequest(BaseModel):
    rating: int = Field(..., ge=0, le=5)  # Rating between 0-5
    review: str = ""  # Review explaining the rating

class WatchlistRequest(BaseModel):
    watched_status: str

# To send a combination of all three request models when the user fills out the form
class RequestMovieWithWatchStatusAndReview(BaseModel):
    movie: MovieRequest
    watchlist: WatchlistRequest
    review: ReviewRequest


# MongoDB Document Models
class Movie(Document):
    title: str
    comment: str = ""
    added_by: str = "anonymous"  # Username of who added the movie
    date_added: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "movies"  # Collection name

class Review(Document):
    movie_id: str  # Reference to Movie.id
    user_id: str  # Reference to User.id (this links the review to a user)
    rating: int = Field(..., ge=0, le=5)  # Rating between 0-5
    review: str = ""  # Review explaining the rating
    date_added: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "reviews"  # Collection name

class Watchlist(Document):
    id: str
    watched_id: str  # Reference to Movie.id
    user_id: str  # Reference to User.id (this links the movie to the user’s watchlist)
    watched_status: str
    date_added: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "watchlist"  # Collection name

# Response Models (for API output)
class MovieResponse(BaseModel):
    id: str
    title: str
    comment: Optional[str] = ""
    review: Optional[str] = ""
    added_by: str
    rating: Optional[float] = 0
    date_added: Optional[datetime] = None
    watched_status: Optional[str] = "not_watched"
    is_admin: Optional[bool] = False

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
