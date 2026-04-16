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


class CategoriesResponse(BaseModel):
    status: str
    categories: List[str]
    category_count: int


class ErrorResponse(BaseModel):
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str  # e.g., "ok"
    app_name: str
    version: str
    jokes_loaded: bool
    joke_count: int
    category_count: int
    environment: str | None = None
