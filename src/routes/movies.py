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
            "<h2>Fetches a paginated list of movies from the database. "
            "You can specify the page number and the number of items per page. "
            "The response includes movie details, total pages, and total items, "
            "as well as links to the previous and next pages if applicable.</h2>"
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
):
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
        "<h2>Fetches detailed information about a movie by its ID. "
        "The response includes all details about the movie, such as name, genre, "
        "overview, crew, and other metadata.</h2>"
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
):
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie with the given ID was not found."
        )

    return MovieDetailResponseSchema.model_validate(movie)
