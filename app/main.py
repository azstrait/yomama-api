import logging
from logging.config import dictConfig
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from pathlib import Path
from fastapi_swagger_ui_theme import setup_swagger_ui_theme

from .models import JokeResponse, CategoriesResponse, ErrorResponse, HealthResponse
from .data_loader import JokeDataStore
from .config import get_settings

settings = get_settings()

# --- Logging configuration ---
LOG_LEVEL = settings.LOG_LEVEL.upper()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # keep stdlib loggers, but we reconfigure them
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"],
    },
    # Optionally tune specific loggers
    "loggers": {
        # Reduce noise from uvicorn access log (we'll also disable access-log below)
        "uvicorn.access": {"level": "WARNING"},
        # Application logger (we'll use app_logger = logging.getLogger("yomama"))
        "yomama": {"level": LOG_LEVEL, "handlers": ["console"], "propagate": False},
    },
}

dictConfig(LOGGING_CONFIG)

app_logger = logging.getLogger("yomama")
# --- end logging configuration ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context: runs at startup/shutdown.
    """
    try:
        joke_store.load_from_file()
        app_logger.info("Jokes list loaded successfully.")
    except Exception as exc:  # pylint: disable=broad-except
        app_logger.exception("Failed to load jokes list: %s", exc)
        # Let the app fail fast if we can't load data
        raise RuntimeError(f"Failed to load jokes list: {exc}") from exc
    yield


app = FastAPI(
    title="Yo Mama Jokes API",
    description='RESTful Web App and API for "Yo Mama" Jokes!',
    version="1.0.0",
    openapi_tags=[
        {"name": "Jokes", "description": "Endpoints for getting jokes and categories."},
        {"name": "System", "description": "Health and system-related endpoints."},
    ],
    docs_url=None,
    lifespan=lifespan,
)

setup_swagger_ui_theme(
    app,
    docs_path="/docs",
    title="Yo Mama Jokes API",
    static_mount_path="/swagger-ui-theme-static",
    swagger_favicon_url=None,
    oauth2_redirect_url=None,
    init_oauth=None,
    swagger_ui_parameters={
        "docExpansion": "list",
        "apis": "ApisPreset",
        "defaultModelsExpandDepth": "1",
    },
)

joke_store = JokeDataStore()

# Templates and static files
templates = Jinja2Templates(directory=str(settings.BASE_DIR / "app" / "templates"))
app.mount(
    "/static",
    StaticFiles(directory=str(settings.BASE_DIR / "app" / "static")),
    name="static",
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request) -> HTMLResponse:
    """
    Render the homepage.
    The actual HTML/JS calls the API endpoints.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "expose_jokes_file": settings.DOWNLOADABLE_JOKES,
        },
        status_code=200,
    )


@app.get("/data/jokes", include_in_schema=False)
async def get_jokes_file():
    """
    Serve the jokes file (CSV or TSV) so users can browse/download the full list.
    The browser should render it inline rather than force a download.
    """
    current_settings = get_settings()
    if not current_settings.DOWNLOADABLE_JOKES:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Not found")

    csv_path = current_settings.DATA_DIR / current_settings.JOKES_CSV_FILENAME
    tsv_path = current_settings.DATA_DIR / current_settings.JOKES_TSV_FILENAME

    file_path: Path | None = None
    media_type = "text/plain"

    if csv_path.is_file():
        file_path = csv_path
        media_type = "text/csv"
    elif tsv_path.is_file():
        file_path = tsv_path
        media_type = "text/tab-separated-values"

    if file_path is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="No jokes file found on server",
        )

    return FileResponse(
        path=file_path,
        media_type=media_type,
    )


@app.get(
    "/api/random",
    response_model=JokeResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "No jokes found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "failure",
                        "message": "No jokes found",
                    }
                }
            },
        },
    },
    tags=["Jokes"],
)
async def get_random_joke() -> JokeResponse:
    """
    Get a random joke from any category.
    """
    try:
        joke = joke_store.get_random_joke()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get random joke: {exc}",
        ) from exc

    if joke is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="No jokes found",
        )

    return JokeResponse(
        status="success",
        id=joke.id,
        joke=joke.joke,
        category=joke.category,
    )


@app.get(
    "/api/random/{category}",
    response_model=JokeResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Category not found or has no jokes",
            "content": {
                "application/json": {
                    "example": {
                        "status": "failure",
                        "message": "Category not found or has no jokes",
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": "Invalid category",
            "content": {
                "application/json": {
                    "example": {
                        "status": "failure",
                        "message": "Invalid category supplied",
                    }
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "failure",
                        "message": "Internal server error",
                    }
                }
            },
        },
    },
    tags=["Jokes"],
)
async def get_random_joke_by_category(category: str) -> JokeResponse:
    """
    Get a random joke from a specific category.
    """
    try:
        found, joke = joke_store.get_random_joke_by_category(category)
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get random joke by category: {exc}",
        ) from exc

    if not found or joke is None:
        # Category not found or empty
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Category not found or has no jokes",
        )

    return JokeResponse(
        status="success",
        id=joke.id,
        joke=joke.joke,
        category=joke.category,
    )


@app.get(
    "/api/categories",
    response_model=CategoriesResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "No categories found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "failure",
                        "message": "No categories found",
                    }
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "failure",
                        "message": "Internal server error",
                    }
                }
            },
        },
    },
    tags=["Jokes"],
)
async def get_categories() -> CategoriesResponse:
    """
    Get a list of all categories.
    """
    try:
        categories = joke_store.get_categories()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categories: {exc}",
        ) from exc

    if not categories:  # empty list or None => 404
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="No categories found",
        )

    category_count = len(categories)  # or joke_store.get_category_count()

    return CategoriesResponse(
        status="success",
        categories=categories,
        category_count=category_count,
    )


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health() -> HealthResponse:
    """
    Basic health check: reports app status and whether jokes are loaded.
    """
    try:
        categories = joke_store.get_categories()
        category_count = len(categories)
        jokes_loaded = category_count > 0
        joke_count = len(joke_store._all_jokes) if jokes_loaded else 0  # type: ignore[attr-defined]
    except Exception:
        jokes_loaded = False
        joke_count = 0
        category_count = 0

    env = None

    return HealthResponse(
        status="ok" if jokes_loaded else "degraded",
        app_name=app.title,
        version=app.version,
        jokes_loaded=jokes_loaded,
        joke_count=joke_count,
        category_count=category_count,
        environment=env,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Convert HTTPExceptions into our ErrorResponse format.
    Avoid logging request details (no IP/body).
    """
    message = exc.detail if isinstance(exc.detail, str) else "An error occurred"

    # Log only the status and message (no request info)
    app_logger.warning("HTTPException: status=%s message=%s", exc.status_code, message)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(status="failure", message=message).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    app_logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="failure",
            message="Internal server error",
        ).model_dump(),
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Remove the default validation error schemas if present
    components = openapi_schema.get("components", {})
    schemas = components.get("schemas", {})
    for name in ["HTTPValidationError", "ValidationError"]:
        schemas.pop(name, None)

    # Inject enum values for /api/random/{category} based on loaded categories
    try:
        categories = joke_store.get_categories()
    except Exception:
        categories = []

    if categories:
        paths = openapi_schema.get("paths", {})
        random_cat_path = paths.get("/api/random/{category}")
        if random_cat_path:
            for method_conf in random_cat_path.values():
                parameters = method_conf.get("parameters", [])
                for param in parameters:
                    if param.get("name") == "category" and "schema" in param:
                        param_schema = param["schema"]
                        # Set enum to the list of categories
                        param_schema["enum"] = categories
                        # if categories:
                        #     param_schema.setdefault("example", categories[0])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
