from pydantic import BaseModel
from typing import Optional


class Movie(BaseModel):
    id: int
    title: str
    comment: str
    rating: int
    watched: bool = False


class MovieRequest(BaseModel):
    title: str
    comment: str
    rating: int
    watched: bool = False
