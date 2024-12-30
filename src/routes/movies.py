from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, MovieModel

from schemas import (
    MovieDetailResponseSchema,
    MovieListResponseSchema
)

router = APIRouter()


@router.get(
    "/movies/",
    response_model=MovieListResponseSchema,
    summary="Get a paginated list of movies",
    description=(
            "<h3>This endpoint retrieves a paginated list of movies from the database. "
            "Clients can specify the `page` number and the number of items per page using `per_page`. "
            "The response includes details about the movies, total pages, and total items, "
            "along with links to the previous and next pages if applicable.</h3>"
    ),
    responses={
        404: {
            "description": "No movies found.",
            "content": {
                "application/json": {
                    "example": {"detail": "No movies found."}
                }
            },
        }
    }
)
def get_movie_list(
        page: int = Query(1, ge=1, description="Page number (1-based index)"),
        per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
        db: Session = Depends(get_db),
) -> MovieListResponseSchema:
    """
    Fetch a paginated list of movies from the database.

    This function retrieves a paginated list of movies, allowing the client to specify
    the page number and the number of items per page. It calculates the total pages
    and provides links to the previous and next pages when applicable.

    :param page: The page number to retrieve (1-based index, must be >= 1).
    :type page: int
    :param per_page: The number of items to display per page (must be between 1 and 20).
    :type per_page: int
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: Session

    :return: A response containing the paginated list of movies and metadata.
    :rtype: MovieListResponseSchema

    :raises HTTPException: Raises a 404 error if no movies are found for the requested page.

    Response Schema:
        - movies: A list of movie details for the current page.
        - prev_page: A URL for the previous page, if applicable.
        - next_page: A URL for the next page, if applicable.
        - total_pages: The total number of pages available.
        - total_items: The total number of movies in the database.
    """
    offset = (page - 1) * per_page

    query = db.query(MovieModel)
    total_items = query.count()
    movies = query.offset(offset).limit(per_page).all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    movie_details = [MovieDetailResponseSchema.model_validate(movie) for movie in movies]

    total_pages = (total_items + per_page - 1) // per_page

    response = MovieListResponseSchema(
        movies=movie_details,
        prev_page=f"/theater/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        next_page=f"/theater/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        total_pages=total_pages,
        total_items=total_items,
    )
    return response


@router.get(
    "/movies/{movie_id}/",
    response_model=MovieDetailResponseSchema,
    summary="Get movie details by ID",
    description=(
            "<h3>Fetch detailed information about a specific movie by its unique ID. "
            "This endpoint retrieves all available details for the movie, such as "
            "its name, genre, crew, budget, and revenue. If the movie with the given "
            "ID is not found, a 404 error will be returned.</h3>"
    ),
    responses={
        404: {
            "description": "Movie not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie with the given ID was not found."}
                }
            },
        }
    }
)
def get_movie_by_id(
        movie_id: int,
        db: Session = Depends(get_db),
) -> MovieDetailResponseSchema:
    """
        Retrieve detailed information about a specific movie by its ID.

        This function fetches detailed information about a movie identified by its unique ID.
        If the movie does not exist, a 404 error is returned.

        :param movie_id: The unique identifier of the movie to retrieve.
        :type movie_id: int
        :param db: The SQLAlchemy database session (provided via dependency injection).
        :type db: Session

        :return: The details of the requested movie.
        :rtype: MovieDetailResponseSchema

        :raises HTTPException: Raises a 404 error if the movie with the given ID is not found.

        Response Schema:
            - id: The unique identifier of the movie.
            - name: The name of the movie.
            - date: The release date of the movie.
            - score: The movie's score or rating.
            - genre: The genres associated with the movie.
            - overview: A brief overview of the movie.
            - crew: The list of crew members involved in the movie.
            - orig_title: The original title of the movie.
            - status: The status of the movie (e.g., released).
            - orig_lang: The original language of the movie.
            - budget: The movie's budget.
            - revenue: The revenue generated by the movie.
            - country: The country of origin.
    """
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie with the given ID was not found."
        )

    return MovieDetailResponseSchema.model_validate(movie)
