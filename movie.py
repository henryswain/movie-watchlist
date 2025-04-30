from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, status, Query
from movie_model import (
    Movie, MovieRequest, MovieResponse,
    Review, ReviewRequest, ReviewResponse, 
    Watchlist, WatchlistRequest, WatchlistResponse
)
from jwt_auth import get_current_user, TokenData
from datetime import datetime
from beanie import PydanticObjectId

movie_router = APIRouter()

# ----- MOVIE ENDPOINTS -----

@movie_router.post("", status_code=status.HTTP_201_CREATED, response_model=Movie)
async def add_movie(
    movie_data: MovieRequest,
    current_user: Optional[TokenData] = Depends(get_current_user)
) -> Movie:
    """Add a new movie to the database"""
    print("Adding movie:", movie_data)
    
    # Create new movie document
    new_movie = Movie(
        title=movie_data.title,
        comment=movie_data.comment,
        review=movie_data.review,  # Include review in movie document
        added_by=current_user.username if current_user else "anonymous",
        date_added=datetime.now()
    )
    
    # Save to database
    await new_movie.insert()
    print("Movie saved with ID:", new_movie.id)
    
    # If the movie has a rating and the user is logged in, create a review
    if movie_data.rating > 0 and current_user:
        # Create review document
        new_review = Review(
            movie_id=str(new_movie.id),
            user_id=current_user.username,
            rating=movie_data.rating,
            review=movie_data.review,
            date_added=datetime.now()
        )
        await new_review.insert()
        print("Review saved with ID:", new_review.id)
    
    return new_movie

@movie_router.get("", response_model=List[MovieResponse])
async def get_movies(
    current_user: Optional[TokenData] = Depends(get_current_user)
) -> List[MovieResponse]:
    """Get all movies with optional user-specific data"""
    print("Getting all movies")
    
    # Get all movies from database
    movies = await Movie.find_all().to_list()
    movie_responses = []
    
    for movie in movies:
        # Create base response
        movie_response = MovieResponse(
            id=str(movie.id),
            title=movie.title,
            comment=movie.comment,
            review=movie.review,  # Include review in the response
            added_by=movie.added_by,
            date_added=movie.date_added
        )
        
        # Add average rating from all reviews
        reviews = await Review.find(Review.movie_id == str(movie.id)).to_list()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            movie_response.avg_rating = total_rating / len(reviews)
        
        # If user is logged in, add their specific data
        if current_user:
            # Get user's review if any
            user_review = await Review.find_one(
                Review.movie_id == str(movie.id),
                Review.user_id == current_user.username
            )
            if user_review:
                movie_response.user_review = user_review
            
            # Get user's watchlist status if any
            watchlist_entry = await Watchlist.find_one(
                Watchlist.movie_id == str(movie.id),
                Watchlist.user_id == current_user.username
            )
            if watchlist_entry:
                movie_response.watchlist_status = watchlist_entry
        
        movie_responses.append(movie_response)
    
    return movie_responses

@movie_router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_by_id(
    movie_id: str = Path(..., description="The ID of the movie to retrieve"),
    current_user: Optional[TokenData] = Depends(get_current_user)
) -> MovieResponse:
    """Get a specific movie by ID with optional user-specific data"""
    print(f"Getting movie with ID: {movie_id}")
    
    # Get movie from database
    movie = await Movie.get(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found"
        )
    
    # Create base response
    movie_response = MovieResponse(
        id=str(movie.id),
        title=movie.title,
        comment=movie.comment,
        review=movie.review,  # Include review in the response
        added_by=movie.added_by,
        date_added=movie.date_added
    )
    
    # Add average rating from all reviews
    reviews = await Review.find(Review.movie_id == movie_id).to_list()
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        movie_response.avg_rating = total_rating / len(reviews)
    
    # If user is logged in, add their specific data
    if current_user:
        # Get user's review if any
        user_review = await Review.find_one(
            Review.movie_id == movie_id,
            Review.user_id == current_user.username
        )
        if user_review:
            movie_response.user_review = user_review
        
        # Get user's watchlist status if any
        watchlist_entry = await Watchlist.find_one(
            Watchlist.movie_id == movie_id,
            Watchlist.user_id == current_user.username
        )
        if watchlist_entry:
            movie_response.watchlist_status = watchlist_entry
    
    return movie_response


@movie_router.put("/{movie_id}", response_model=Movie)
async def update_movie(
    movie_data: MovieRequest,
    movie_id: str = Path(..., description="The ID of the movie to update"),
    current_user: Optional[TokenData] = Depends(get_current_user)
) -> Movie:
    """Update an existing movie"""
    print(f"Updating movie with ID: {movie_id}")
    
    # Get movie from database
    movie = await Movie.get(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found"
        )
    
    # Check if user has permission to update (admin or creator)
    if current_user and current_user.username != movie.added_by and current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this movie"
        )
    
    # Update movie fields
    movie.title = movie_data.title
    movie.comment = movie_data.comment
    movie.review = movie_data.review  # Update the review
    
    # Save changes
    await movie.save()
    
    # If the movie has a rating and the user is logged in, update or create a review
    if movie_data.rating > 0 and current_user:
        # Check if user already has a review for this movie
        existing_review = await Review.find_one(
            Review.movie_id == movie_id,
            Review.user_id == current_user.username
        )
        
        if existing_review:
            # Update existing review
            existing_review.rating = movie_data.rating
            existing_review.review = movie_data.review
            await existing_review.save()
            print(f"Review updated for movie ID: {movie_id}")
        else:
            # Create new review
            new_review = Review(
                movie_id=movie_id,
                user_id=current_user.username,
                rating=movie_data.rating,
                review=movie_data.review,
                date_added=datetime.now()
            )
            await new_review.insert()
            print(f"Review created for movie ID: {movie_id}")
    
    return movie


@movie_router.delete("/{movie_id}")
async def delete_movie(
    movie_id: str = Path(..., description="The ID of the movie to delete"),
    current_user: Optional[TokenData] = Depends(get_current_user)
) -> dict:
    """Delete a movie and all associated reviews and watchlist entries"""
    print(f"Deleting movie with ID: {movie_id}")
    
    # Get movie from database
    movie = await Movie.get(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found"
        )
    
    # Check if user has permission to delete (admin or creator)
    if current_user and current_user.username != movie.added_by and current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this movie"
        )
    
    # Delete movie
    await movie.delete()
    
    # Delete associated reviews
    await Review.find(Review.movie_id == movie_id).delete()
    
    # Delete associated watchlist entries
    await Watchlist.find(Watchlist.movie_id == movie_id).delete()
    
    return {"message": f"Movie with ID={movie_id} and all associated data deleted successfully"}


# ----- REVIEW ENDPOINTS -----

@movie_router.post("/{movie_id}/reviews", status_code=status.HTTP_201_CREATED, response_model=Review)
async def add_review(
    review_data: ReviewRequest,
    movie_id: str = Path(..., description="The ID of the movie to review"),
    current_user: Optional[TokenData] = Depends(get_current_user)
) -> Review:
    """Add or update a review for a movie"""
    print(f"ADD REVIEW ENDPOINT CALLED for movie ID: {movie_id}")
    print(f"Review data: {review_data}")
    print(f"Current user: {current_user}")
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to add a review"
        )
    
    # Verify movie exists
    movie = await Movie.get(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found"
        )
    
    # Check if user already has a review for this movie
    existing_review = await Review.find_one(
        Review.movie_id == movie_id,
        Review.user_id == current_user.username
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
            date_added=datetime.now()
        )
        await new_review.insert()
        print(f"New review created with ID: {new_review.id}")
        return new_review