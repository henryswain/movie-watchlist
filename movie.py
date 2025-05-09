from typing import List, Optional, Annotated
from bson import ObjectId

from fastapi import APIRouter, Depends, File, Path, HTTPException, UploadFile, status, Query
from fastapi.responses import JSONResponse
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
from logging_config import setup_logger
import base64
from user_model import User

logger = setup_logger()

movie_router = APIRouter()

# ----- MOVIE ENDPOINTS -----
import base64

@movie_router.get("/get-background-photo")
async def get_background_photo(
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> dict:
    user_data = await User.find_one({"username": current_user.username})
    
    if user_data and hasattr(user_data, "photo") and user_data.photo:
        # If the photo doesn't already have the data URI prefix, add it
        photo = user_data.photo
        if not photo.startswith('data:image'):
            # Determine the image type if possible, or default to JPEG
            image_type = "jpeg"
            photo = f"data:image/{image_type};base64,{photo}"
        
        return {"photo": photo}
    return {"photo": ""}

@movie_router.post("/upload-background-photo")
async def upload_background_photo(
    photo: UploadFile = File(...),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> dict:
    contents = await photo.read()
    encoded_photo = base64.b64encode(contents).decode('utf-8')

    user_data = await User.find_one({"username": current_user.username})
    user_data.photo = encoded_photo
    await user_data.save()

    return {"message": "Photo uploaded successfully"}

@movie_router.post("", status_code=status.HTTP_201_CREATED, response_model=Movie)
async def add_movie(
    payload: RequestMovieWithWatchStatusAndReview,
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> Movie:
    """Add a new movie to the database"""

    # extract each section of data
    movie_data = payload.movie
    review_data = payload.review
    watchlist_data = payload.watchlist

    # Create new movie document
    new_movie = Movie(
        title=movie_data.title,
        comment=movie_data.comment,
        added_by=current_user.username if current_user else "anonymous",
        date_added=datetime.now(),
    )

    # Save to database
    await new_movie.insert()

    # Log movie addition
    role = current_user.role if current_user else "Anonymous"
    username = current_user.username if current_user else "anonymous"
    logger.info(f"Movie '{movie_data.title}' added by user '{username}'. Role: {role} ")

    # If the user is logged in, create a review
    if current_user:
        # Create review document
        new_review = Review(
            movie_id=str(new_movie.id),
            user_id=current_user.username,
            rating=review_data.rating,
            review=review_data.review,
            date_added=datetime.now(),
        )
        await new_review.insert()
        logger.info(
            f"Review added for movie '{movie_data.title}' by user '{current_user.username}'. Rating: {review_data.rating}"
        )

    # update watchlist
    new_watchlist_indicator = Watchlist(
        id=str(new_movie.id),
        watched_id=str(new_movie.id),
        user_id=current_user.username,
        watched_status=watchlist_data.watched_status,
    )
    await new_watchlist_indicator.insert()
    return new_movie


@movie_router.get("/{watched_status}", response_model=List[MovieResponse])
async def get_movies(
    watched_status: str = Path(..., description="The ID of the movie to retrieve"),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> List[MovieResponse]:
    """Get all movies with optional user-specific data"""
    try:
        # get watched data based on watched_status
        watched_information = []
        if watched_status == "all":
            # For "all", show all movies in the database
            watched_information = await Watchlist.find_all().to_list()
        elif watched_status == "my":
            # For "my", show movies added by the current user
            watched_information = await Watchlist.find(
                {"user_id": current_user.username}
            ).to_list()
        elif watched_status in ["watched", "not_watched"]:
            # For "watched"/"not_watched", filter by both status AND current user
            watched_information = await Watchlist.find(
                {"watched_status": watched_status, "user_id": current_user.username}
            ).to_list()
        else:
            # Fallback for any other status
            watched_information = await Watchlist.find(
                {"watched_status": watched_status}
            ).to_list()

        # Create a dictionary to map movie IDs to their watched status
        watchlist_map = {
            doc.watched_id: doc.watched_status for doc in watched_information
        }

        watched_ids_as_objects = [
            ObjectId(doc.watched_id) for doc in watched_information
        ]

        # get movies with the gathered watched information
        movies = await Movie.find({"_id": {"$in": watched_ids_as_objects}}).to_list()
        movie_responses = []

        for movie in movies:
            # get review data
            review = await Review.find_one({"movie_id": str(movie.id)})
            if not review:
                # Handle case where a movie doesn't have a review
                logger.warning(f"No review found for movie {movie.id} - {movie.title}")
                review_text = ""
                rating = 0
            else:
                review_text = review.review
                rating = review.rating

            # Get watched status from the map, default to "not_watched"
            movie_watched_status = watchlist_map.get(str(movie.id), "not_watched")

            movie_response = MovieResponse(
                id=str(movie.id),
                title=movie.title,
                comment=movie.comment,
                review=review_text,
                added_by=movie.added_by,
                rating=rating,
                date_added=movie.date_added,
                watched_status=movie_watched_status,  # Include the watched status
            )

            movie_responses.append(movie_response)

        return movie_responses

    except Exception as e:
        # Log the error and return a more helpful message
        logger.error(f"Error in get_movies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting movies: {str(e)}",
        )


@movie_router.get("/get/{movie_id}", response_model=MovieResponse)
async def get_movie_by_id(
    movie_id: str = Path(..., description="The ID of the movie to retrieve"),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> MovieResponse:
    """Get a specific movie by ID with optional user-specific data"""

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
        is_admin=is_admin,
    )
    return movie_response


@movie_router.put("/{movie_id}", response_model=Movie)
async def update_movie(
    payload: RequestMovieWithWatchStatusAndReview,
    movie_id: str = Path(..., description="The ID of the movie to update"),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> Movie:
    """Update an existing movie"""

    # extract each section of data
    watchlist_data = payload.watchlist
    review_data = payload.review
    movie_data = payload.movie

    # Get movie from database
    movie = await Movie.get(movie_id)
    if not movie:
        logger.error(f"Update movie failed: Movie with ID={movie_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found",
        )

    # Check permissions - allow only if user is admin or the movie creator
    if current_user:
        # Get user to check if admin
        user = await User.find_one({"username": current_user.username})
        is_admin = user and user.role == "AdminUser"

        # If not admin and not the creator, forbid the action
        if not is_admin and movie.added_by != current_user.username:
            logger.warning(
                f"Unauthorized movie edit attempt: User '{current_user.username}' tried to edit movie '{movie.title}' created by '{movie.added_by}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit movies that you created.",
            )

        # Log the edit operation
        admin_str = "Admin " if is_admin else ""
        logger.info(
            f"{admin_str}User '{current_user.username}' edited movie '{movie.title}'. Role: {current_user.role}"
        )
    else:
        logger.error("Unauthenticated movie edit attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to edit movies.",
        )

    # Update movie fields
    movie.title = movie_data.title
    movie.comment = movie_data.comment

    # Save changes
    await movie.save()

    # MODIFIED: Review handling with special admin case
    if review_data.rating > 0:
        if is_admin:
            # If admin, update or create review for the ORIGINAL CREATOR
            # This ensures the review shows up for all users
            existing_review = await Review.find_one(
                Review.movie_id == movie_id,
                Review.user_id == movie.added_by,  # Use movie creator's username
            )

            if existing_review:
                # Update existing review as admin
                existing_review.rating = review_data.rating
                existing_review.review = review_data.review
                await existing_review.save()
                logger.info(
                    f"Admin updated review for movie '{movie.title}' originally added by '{movie.added_by}'. Rating: {review_data.rating}"
                )
            else:
                # Create new review as admin for the original creator
                new_review = Review(
                    movie_id=movie_id,
                    user_id=movie.added_by,  # Use movie creator's username
                    rating=review_data.rating,
                    review=review_data.review,
                    date_added=datetime.now(),
                )
                await new_review.insert()
                logger.info(
                    f"Admin created new review for movie '{movie.title}' on behalf of '{movie.added_by}'. Rating: {review_data.rating}"
                )

            # Also update/create the admin's personal review
            admin_review = await Review.find_one(
                Review.movie_id == movie_id, Review.user_id == current_user.username
            )

            if admin_review:
                admin_review.rating = review_data.rating
                admin_review.review = review_data.review
                await admin_review.save()
            else:
                new_admin_review = Review(
                    movie_id=movie_id,
                    user_id=current_user.username,
                    rating=review_data.rating,
                    review=review_data.review,
                    date_added=datetime.now(),
                )
                await new_admin_review.insert()

        else:
            # Regular user flow - update their own review
            existing_review = await Review.find_one(
                Review.movie_id == movie_id, Review.user_id == current_user.username
            )

            if existing_review:
                # Update existing review
                existing_review.rating = review_data.rating
                existing_review.review = review_data.review
                await existing_review.save()
                logger.info(
                    f"Review updated for movie '{movie.title}' by user '{current_user.username}'. Rating: {review_data.rating}"
                )
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
                logger.info(
                    f"New review added for movie '{movie.title}' by user '{current_user.username}'. Rating: {review_data.rating}"
                )

    # Watchlist handling code remains unchanged
    try:
        # First check for ANY watchlist entry for this movie
        existing_watchlists = await Watchlist.find({"watched_id": movie_id}).to_list()

        # Check if there's an entry specifically for this user
        user_watchlist = None
        for watchlist in existing_watchlists:
            if watchlist.user_id == current_user.username:
                user_watchlist = watchlist
                break

        if user_watchlist:
            # Update existing watchlist entry for this user
            user_watchlist.watched_status = watchlist_data.watched_status
            await user_watchlist.save()
            logger.info(
                f"Watchlist updated for movie '{movie.title}' by user '{current_user.username}'. Status: {watchlist_data.watched_status}"
            )
        else:
            # Generate a truly unique ID using an ObjectId
            from bson import ObjectId

            unique_id = str(ObjectId())

            # Create new watchlist entry with the unique ID
            new_watchlist = Watchlist(
                id=unique_id,  # Use a completely new ID
                watched_id=movie_id,
                user_id=current_user.username,
                watched_status=watchlist_data.watched_status,
                date_added=datetime.now(),
            )
            await new_watchlist.insert()
            logger.info(
                f"New watchlist entry created for movie '{movie.title}' by user '{current_user.username}'. Status: {watchlist_data.watched_status}"
            )
    except Exception as e:
        error_message = f"Error updating watchlist for movie '{movie.title}': {str(e)}"
        logger.error(error_message)
        # Continue execution rather than crashing

    return movie


@movie_router.delete("/{movie_id}")
async def delete_movie(
    movie_id: str = Path(..., description="The ID of the movie to delete"),
    current_user: Optional[TokenData] = Depends(get_current_user),
) -> dict:
    """Delete a movie and all associated reviews and watchlist entries"""
    print(f"Deleting movie with ID: {movie_id}")

    # Get movie from database
    movie = await Movie.get(ObjectId(movie_id))
    if not movie:
        logger.error(f"Delete movie failed: Movie with ID={movie_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID={movie_id} not found",
        )

    # Check permissions - allow only if user is admin or the movie creator
    if current_user:
        # Get user to check if admin
        user = await User.find_one({"username": current_user.username})
        is_admin = user and user.role == "AdminUser"

        # If not admin and not the creator, forbid the action
        if not is_admin and movie.added_by != current_user.username:
            logger.warning(
                f"Unauthorized movie delete attempt: User '{current_user.username}' tried to delete movie '{movie.title}' created by '{movie.added_by}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete movies that you created.",
            )

        # Log the delete operation
        admin_str = "Admin " if is_admin else ""
        logger.info(
            f"{admin_str}User '{current_user.username}' deleted movie '{movie.title}'. Role: {current_user.role}"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to delete movies.",
        )

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
