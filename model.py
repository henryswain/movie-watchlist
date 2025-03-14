from pydantic import BaseModel
from typing import Optional


class Movie(BaseModel):
    id: int
    title: str
    director: str
    release_year: int
    watched: bool = False


class MovieRequest(BaseModel):
    title: str
    director: str
    release_year: int
    watched: bool = False
