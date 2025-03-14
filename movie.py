from fastapi import APIRouter, Path, HTTPException, status
from model import Movie, MovieRequest
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

movie_router = APIRouter()

movie_list = []
max_id: int = 0


@movie_router.post("", status_code=status.HTTP_201_CREATED)
async def add_movie(movie: MovieRequest) -> Movie:
    global max_id
    max_id += 1  # auto increment ID
    new_movie = Movie(
        id=max_id,
        title=movie.title,
        director=movie.director,
        release_year=movie.release_year,
        watched=movie.watched,
    )
    movie_list.append(new_movie)
    return new_movie


@movie_router.get("")
async def get_movies() -> list[Movie]:
    return movie_list


@movie_router.get("/{id}")
async def get_movie_by_id(id: int = Path(..., title="default")) -> Movie:
    for movie in movie_list:
        if movie.id == id:
            return movie
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"The movie with ID={id} is not found.",
    )


@movie_router.put("/{id}")
async def update_movie(movie: MovieRequest, id: int) -> dict:
    for x in movie_list:
        if x.id == id:
            x.title = movie.title
            x.director = movie.director
            x.release_year = movie.release_year
            x.watched = movie.watched
            return {"message": "Movie updated successfully"}
    return {"message": f"The movie with ID={id} is not found."}


@movie_router.delete("/{id}")
async def delete_movie(id: int) -> dict:
    for i in range(len(movie_list)):
        movie = movie_list[i]
        if movie.id == id:
            movie_list.pop(i)
            return {"message": f"The movie with ID={id} has been deleted."}
    return {"message": f"The movie with ID={id} is not found."}


@movie_router.put("/{id}/toggle-watched")
async def toggle_watched(id: int) -> dict:
    for movie in movie_list:
        if movie.id == id:
            movie.watched = not movie.watched
            return {
                "message": f"Movie with ID={id} watched status toggled to {movie.watched}"
            }
    return {"message": f"The movie with ID={id} is not found."}
