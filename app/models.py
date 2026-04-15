from pydantic import BaseModel
from typing import List


class Joke(BaseModel):
    id: int
    joke: str
    category: str


class JokeResponse(BaseModel):
    status: str
    id: int
    joke: str
    category: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "id": 42,
                "joke": "Yo mama is so old, her first car was a chariot.",
                "category": "old",
            }
        }
    }


class CategoriesResponse(BaseModel):
    status: str
    categories: List[str]
    category_count: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "categories": ["fat", "stupid", "ugly"],
                "category_count": 3,
            }
        }
    }


class ErrorResponse(BaseModel):
    status: str
    message: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "failure",
                "message": "Category not found or has no jokes",
            }
        }
    }


class HealthResponse(BaseModel):
    status: str  # e.g., "ok"
    app_name: str
    version: str
    jokes_loaded: bool
    joke_count: int
    category_count: int
    environment: str | None = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "app_name": "Yo Mama Jokes API",
                "version": "1.0.0",
                "jokes_loaded": True,
                "joke_count": 123,
                "category_count": 3,
                "environment": "production",
            }
        }
    }
