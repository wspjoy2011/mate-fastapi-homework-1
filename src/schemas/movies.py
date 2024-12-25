from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MovieBaseSchema(BaseModel):
    name: str = Field(..., max_length=255)
    date: date
    score: float = Field(..., ge=0)
    genre: str = Field(..., max_length=255)
    overview: str
    crew: str
    orig_title: str = Field(..., max_length=255)
    status: str = Field(..., max_length=50)
    orig_lang: str = Field(..., max_length=50)
    budget: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    country: str = Field(..., max_length=3)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Creed III",
                    "date": "2023-03-02",
                    "score": 73,
                    "genre": "Drama,Action",
                    "overview": "After dominating the boxing world, Adonis Creed has been thriving in both his "
                                "career and family life...",
                    "crew": "Michael B. Jordan, Tessa Thompson",
                    "orig_title": "Creed III",
                    "status": "Released",
                    "orig_lang": "English",
                    "budget": 75000000,
                    "revenue": 271616668,
                    "country": "AU"
                }
            ]
        }
    }

    @field_validator('date')
    @classmethod
    def validate_date(cls, value):
        current_year = datetime.now().year
        if value.year > current_year + 1:
            raise ValueError(f"The year in 'date' cannot be greater than {current_year + 1}.")
        return value


class MovieDetailResponseSchema(MovieBaseSchema):
    id: int


class MovieListResponseSchema(BaseModel):
    movies: list[MovieDetailResponseSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "movies": [
                        {
                            "id": 1,
                            "name": "Creed III",
                            "date": "2023-03-02",
                            "score": 73,
                            "genre": "Drama,Action",
                            "overview": "After dominating the boxing world, Adonis Creed has been thriving in both "
                                        "his career and family life...",
                            "crew": "Michael B. Jordan, Tessa Thompson",
                            "orig_title": "Creed III",
                            "status": "Released",
                            "orig_lang": "English",
                            "budget": 75000000,
                            "revenue": 271616668,
                            "country": "AU"
                        }
                    ],
                    "prev_page": "/theater/movies/?page=1&per_page=10",
                    "next_page": "/theater/movies/?page=3&per_page=10",
                    "total_pages": 1000,
                    "total_items": 9999
                }
            ]
        }
    }
