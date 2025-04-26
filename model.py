from beanie import Document
from pydantic import BaseModel
from typing import Optional


class Movie(Document):
    # id: int
    title: str
    comment: str
    rating: int
    watched: bool = False
    created_by: str

    class settings:
        name = "movies"


class MovieRequest(BaseModel):
    title: str
    comment: str
    rating: int
    watched: bool = False


class Review(Document):
    id: int
    rating: int
    review: str

    class settings:
        name = "reviews"

class ReviewRequest(BaseModel):
    rating: int
    review: str
