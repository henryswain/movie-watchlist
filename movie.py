from typing import List, Optional, Annotated
from bson import ObjectId

from fastapi import APIRouter, Depends, Path, HTTPException, status, Query
from movie_model import (
    Movie,
    MovieRequest,
    MovieResponse,
    RequestMovieWithWatchStatusAndReview,
    Review,
    ReviewRequest,
    ReviewResponse,
    Watchlist,
    WatchlistRequest,
    WatchlistResponse,
)
from jwt_auth import get_current_user, TokenData
from datetime import datetime
from beanie import PydanticObjectId

from user_model import User

movie_router = APIRouter()

# ----- MOVIE ENDPOINTS -----


@movie_router.post("", status_code=status.HTTP_201_CREATED, response_model=Movie)
async def add_movie(
    payload: RequestMovieWithWatchStatusAndReview,
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> Movie:
    """Add a new movie to the database"""
    # print("Adding movie:", movie_data)
    print("payload: ", payload)
    print("payload.movie: ", payload.movie)
    print("payload.watchlist: ", payload.watchlist)
    movie_data = payload.movie
    review_data = payload.review
    watchlist_data = payload.watchlist
    # Create new movie document
    new_movie = Movie(
        title=movie_data.title,
        comment=movie_data.comment,
        # review=movie_data.review,  # Include review in movie document
        added_by=current_user.username if current_user else "anonymous",
        date_added=datetime.now(),
    )

    # Save to database
    await new_movie.insert()
    print("Movie saved with ID:", new_movie.id)

    # If the movie has a rating and the user is logged in, create a review
    if review_data.rating > 0 and current_user:
        # Create review document
        new_review = Review(
            movie_id=str(new_movie.id),
            user_id=current_user.username,
            rating=review_data.rating,
            review=review_data.review,
            date_added=datetime.now(),
        )
        await new_review.insert()
        print("Review saved with ID:", new_review.id)

    

    new_watchlist_indicator = Watchlist(
        id=str(new_movie.id),
        watched_id=str(new_movie.id),
        user_id=current_user.username,
        watched_status=watchlist_data.watched_status
    )
    await new_watchlist_indicator.insert()
    return new_movie


@movie_router.get("/{watched_status}", response_model=List[MovieResponse])
async def get_movies(
    watched_status: str = Path(..., description="The ID of the movie to retrieve"),
    current_user: Optional[TokenData] = Depends(get_current_user)) -> List[MovieResponse]:
    """Get all movies with optional user-specific data"""
    print("get_movies called")

    # get incomplete movie data with proper watched_status
    print("watched_status from url: ", watched_status)
    watched_information = []
    review_information = []
    if watched_status == "all":
        print("watched_status == 'all'")
        watched_information = await Watchlist.find_all().to_list()
    else:
        print("watched_status != 'all")
        watched_information = await Watchlist.find({"watched_status": watched_status}).to_list()
    print("watched_information: ", watched_information)
    # watched_ids = [doc.watched_id for doc in watched_information]    # Get all movies from database
    # print("watched_ids: ", watched_ids)

    watched_ids_as_objects = [ObjectId(doc.watched_id) for doc in watched_information]
    print("watched_ids_as_objects: ", watched_ids_as_objects)
    # reviews = await Review.find({"movie_id": {"$in": watched_ids}}).to_list()
    # print("reviews: ", reviews)
    movies = await Movie.find({"_id": {"$in": watched_ids_as_objects}}).to_list()
    print("movies: ", movies)
    movie_responses = []

    for movie in movies:
        # get review data
        print("movie: ", movie)
        print("movie.id: ", movie.id)
        print("str(movie.id): ", str(movie.id))
        review = await Review.find_one({"movie_id": str(movie.id)})
        print("review: ", review)

        # Create base response
        movie_response = MovieResponse(
            id=str(movie.id),
            title=movie.title,
            comment=movie.comment,
            review=review.review,  # Include review in the response
            added_by=movie.added_by,
            rating=review.rating,
            date_added=movie.date_added,
        )

        # Add average rating from all reviews
        # reviews = await Review.find({"movie_id": str(movie.id)}).to_list()
        # if reviews:
        #     total_rating = sum(review.rating for review in reviews)
        #     movie_response.avg_rating = total_rating / len(reviews)

        # If user is logged in, add their specific data
        # if current_user:
        #     # Get user's review if any
        #     user_review = await Review.find_one({
        #         "movie_id": str(movie.id),
        #         "user_id": current_user.username,
        #     })
        #     if user_review:
        #         movie_response.user_review = user_review

        #     # Get user's watchlist status if any
        #     watchlist_entry = await Watchlist.find_one({
        #         "watched_id": str(movie.id),
        #         "user_id": current_user.username,
        #     })

        #     if watchlist_entry:
        #         movie_response.watchlist_status = watchlist_entry
            
        #     # Add is_admin flag for frontend use
        #     movie_response.is_admin = current_user.role == "AdminUser"

        movie_responses.append(movie_response)

    return movie_responses

@movie_router.get("/get/{movie_id}", response_model=MovieResponse)
async def get_movie_by_id(
    movie_id: str = Path(..., description="The ID of the movie to retrieve"),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> MovieResponse:
    """Get a specific movie by ID with optional user-specific data"""
    print("get_movie_by_id called")
    print(f"Getting movie with ID: {movie_id}")
    
    # Get movie from database
    movie = await Movie.get(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found",
        )
    
    # Set admin status
    is_admin = False
    if current_user:
        user = await User.find_one({"username": current_user.username})
        if user and user.role == "AdminUser":
            is_admin = True
    
    # Initialize with default values
    user_rating = 0
    user_review = ""
    watched_status = None
    
    # Get user's review if logged in
    if current_user:
        review_data = await Review.find_one(
            {"movie_id": movie_id, "user_id": current_user.username}
        )
        if review_data:
            user_rating = review_data.rating
            user_review = review_data.review
            print(f"Found review: {user_rating}, {user_review}")
        
        # Get watchlist status
        watchlist_data = await Watchlist.find_one(
            {"watched_id": movie_id, "user_id": current_user.username}
        )
        if watchlist_data:
            watched_status = watchlist_data.watched_status
            print(f"Watchlist status: {watched_status}")
    
    # Create base response
    movie_response = MovieResponse(
        id=str(movie.id),
        title=movie.title,
        comment=movie.comment,
        rating=user_rating,
        review=user_review,
        added_by=movie.added_by,
        date_added=movie.date_added,
        watched_status=watched_status,
        is_admin=is_admin
    )
    
    # Add average rating from all reviews
    # reviews = await Review.find({"movie_id": movie_id}).to_list()
    # if reviews:
    #     total_rating = sum(review.rating for review in reviews)
    #     movie_response.avg_rating = total_rating / len(reviews)
    
    print(f"Returning movie response: {movie_response}")
    return movie_response



# @movie_router.get("/{movie_id}", response_model=MovieResponse)
# async def get_movie_by_id(
#     movie_id: str = Path(..., description="The ID of the movie to retrieve"),
#     current_user: Optional[TokenData] = Depends(get_current_user),
# ) -> MovieResponse:
#     """Get a specific movie by ID with optional user-specific data"""
#     print(f"Getting movie with ID: {movie_id}")

#     # Get movie from database
#     movie = await Movie.get(movie_id)
#     if not movie:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Movie with ID={movie_id} not found",
#         )

#     isAdmin = False
#     user = await User.find({"username": current_user.username})
#     if user.role == "AdminUser":
#         isAdmin = True
#     review_data = await Review.find({"movie_id": movie_id, "user_id": current_user.username})
#     watchlist_data = await Watchlist.find({"watched_id": movie_id, "user_id": current_user.username})
#     # Create base response
#     print("watchlist_data.watched_status: ", watchlist_data.watched_status)
#     movie_response = MovieResponse(

#         id=str(movie.id),
#         title=movie.title,
#         comment=movie.comment,
#         rating=review_data.rating,
#         review=review_data.review,  # Include review in the response
#         added_by=movie.added_by,
#         date_added=movie.date_added,
#         watched_status=watchlist_data.watched_status,
#         is_admin=isAdmin
#     )

#     # Add average rating from all reviews
#     reviews = await Review.find(Review.movie_id == movie_id).to_list()
#     if reviews:
#         total_rating = sum(review.rating for review in reviews)
#         movie_response.avg_rating = total_rating / len(reviews)

#     # If user is logged in, add their specific data
#     if current_user:
#         # Get user's review if any
#         user_review = await Review.find_one(
#             Review.movie_id == movie_id, Review.user_id == current_user.username
#         )
#         if user_review:
#             movie_response.user_review = user_review

#         # Get user's watchlist status if any
#         watchlist_entry = await Watchlist.find_one(
#             Watchlist.watched_id == movie_id, Watchlist.user_id == current_user.username
#         )
#         if watchlist_entry:
#             movie_response.watchlist_status = watchlist_entry

#         # is_admin flag for frontend use
#         movie_response.is_admin = current_user.role == "AdminUser"

#     return movie_response


@movie_router.put("/{movie_id}", response_model=Movie)
async def update_movie(
    # movie_data: MovieRequest,
    payload: RequestMovieWithWatchStatusAndReview,
    movie_id: str = Path(..., description="The ID of the movie to update"),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> Movie:
    """Update an existing movie"""
    print(f"Updating movie with ID: {movie_id}")

    watchlist_data = payload.watchlist
    print("watchlist_data: ", watchlist_data)

    review_data = payload.review
    print("reveiw_data: ", review_data)

    movie_data = payload.movie
    print("movie_data: ", movie_data)
    # Get movie from database
    movie = await Movie.get(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found",
        )

    # Check if user has permission to update (admin or creator)
    # if (
    #     current_user
    #     and current_user.role != "AdminUser"
    #     and current_user.username != movie.added_by
    # ):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to update this movie",
    #     )

    # Update movie fields
    movie.title = movie_data.title
    movie.comment = movie_data.comment
    # movie.review = movie_data.review  # Update the review

    # Save changes
    await movie.save()

    # If the movie has a rating and the user is logged in, update or create a review
    if review_data.rating > 0 and current_user:
        # Check if user already has a review for this movie
        existing_review = await Review.find_one(
            Review.movie_id == movie_id, Review.user_id == current_user.username
        )

        if existing_review:
            # Update existing review
            existing_review.rating = review_data.rating
            existing_review.review = review_data.review
            await existing_review.save()
            print(f"Review updated for movie ID: {movie_id}")
        else:
            # Create new review
            new_review = Review(
                movie_id=movie_id,
                user_id=current_user.username,
                rating=review_data.rating,
                review=review_data.review,
                date_added=datetime.now(),
            )
            await new_review.insert()
            print(f"Review created for movie ID: {movie_id}")

    existing_watchlist = await Watchlist.find_one({"watched_id": movie_id, "user_id": current_user.username})
    existing_watchlist.watched_status = watchlist_data.watched_status
    await existing_watchlist.save()
    return movie


@movie_router.delete("/{movie_id}")
async def delete_movie(
    movie_id: str = Path(..., description="The ID of the movie to delete"),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> dict:
    """Delete a movie and all associated reviews and watchlist entries"""
    print(f"Deleting movie with ID: {movie_id}")

    # Get movie from database
    movie = await Movie.get(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found",
        )

    # Check if user has permission to delete (admin or creator)
    # if (
    #     current_user
    #     and current_user.role != "AdminUser"
    #     and current_user.username != movie.added_by
    # ):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to delete this movie",
    #     )

    # Delete movie
    await movie.delete()

    # Delete associated reviews
    await Review.find({"movie_id": movie_id}).delete()

    # Delete associated watchlist entries
    await Watchlist.find({"movie_id": movie_id}).delete()

    return {
        "message": f"Movie with ID={movie_id} and all associated data deleted successfully"
    }


# ----- REVIEW ENDPOINTS -----


@movie_router.post(
    "/{movie_id}/reviews", status_code=status.HTTP_201_CREATED, response_model=Review
)
async def add_review(
    review_data: ReviewRequest,
    movie_id: str = Path(..., description="The ID of the movie to review"),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> Review:
    """Add or update a review for a movie"""
    print(f"ADD REVIEW ENDPOINT CALLED for movie ID: {movie_id}")
    print(f"Review data: {review_data}")
    print(f"Current user: {current_user}")

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to add a review",
        )

    # Verify movie exists
    movie = await Movie.get(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found",
        )

    # Check if user already has a review for this movie
    existing_review = await Review.find_one(
        Review.movie_id == movie_id, Review.user_id == current_user.username
    )

    if existing_review:
        # Update existing review
        print(f"Updating existing review: {existing_review.id}")
        existing_review.rating = review_data.rating
        existing_review.review = review_data.review
        await existing_review.save()
        print(f"Review updated successfully")
        return existing_review
    else:
        # Create new review
        print(f"Creating new review")
        new_review = Review(
            movie_id=movie_id,
            user_id=current_user.username,
            rating=review_data.rating,
            review=review_data.review,
            date_added=datetime.now(),
        )
        await new_review.insert()
        print(f"New review created with ID: {new_review.id}")
        return new_review
