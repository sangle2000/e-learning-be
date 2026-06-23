from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend API services for e-Learning Platform",
    version="1.0.0"
)

# Set up CORS middleware to allow requests from client-side origins (like React/Vue/Svelte on port 5173)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API version 1 routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root_redirect():
    """
    Root redirect to welcome message or auto-generated swagger documentation.
    """
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}!",
        "docs_url": "/docs",
        "api_version_v1": f"{settings.API_V1_STR}"
    }
