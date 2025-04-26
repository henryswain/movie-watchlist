from typing import Annotated
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Path, HTTPException, status
from jwt_auth import TokenData
from movie_model import Movie, MovieRequest
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

movie_router = APIRouter()

movie_list = []
max_id: int = 0


@movie_router.post("", status_code=status.HTTP_201_CREATED)
async def add_movie(r: MovieRequest) -> Movie:
    print("add movie called: ", r)
    # global max_id
    # max_id += 1  # auto increment ID
    newMovie = Movie(
        title=r.title,
        comment=r.comment,
    )
    # rating=r.rating,
       # review=movie.review,  # Added review field
    # watched=r.watched,
    # movie_list.append(new_movie)
    await newMovie.save()
    return newMovie


@movie_router.get("")
async def get_movies() -> list[Movie]:
    print("get_movies called")
    # if not user or not user.username:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail=f"Please login.",
    #     )
    # return await Movie.find(Movie.created_by == user.username).to_list()
    return await Movie.find_all().to_list()


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
async def update_movie(movie: MovieRequest, id: PydanticObjectId) -> Movie:
    # for x in movie_list:
    #     if x.id == id:
    #         x.title = movie.title
    #         x.comment = movie.comment
    #         x.rating = movie.rating
    #         x.review = movie.review  # Added review field
    #         x.watched = movie.watched
    #         return {"message": "Movie updated successfully"}
    # return {"message": f"The movie with ID={id} is not found."}
    global max_stop_id
    
    existing_movie= await Movie.get(id)
    if existing_movie:
        existing_movie.title = movie.title
        existing_movie.comment = movie.comment
        await existing_movie.save()
        return existing_movie
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Vacation with ID={id} is not found"
    )


@movie_router.delete("/{id}")
async def delete_movie(id: PydanticObjectId) -> dict:
    # for i in range(len(movie_list)):
    #     movie = movie_list[i]
    #     if movie.id == id:
    #         movie_list.pop(i)
    #         return {"message": f"The movie with ID={id} has been deleted."}
    # return {"message": f"The movie with ID={id} is not found."}
    movie = await Movie.get(id)
    if movie:
        await movie.delete()
        return {"message": "movie deleted"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"The movie with ID={id} is not found.",
    )


@movie_router.put("/{id}/toggle-watched")
async def toggle_watched(id: int) -> dict:
    for movie in movie_list:
        if movie.id == id:
            movie.watched = not movie.watched
            return {
                "message": f"Movie with ID={id} watched status toggled to {movie.watched}"
            }
    return {"message": f"The movie with ID={id} is not found."}