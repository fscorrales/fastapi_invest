from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.routes import auth_router
from .iol.routes import iol_router
from .rava.routes import rava_router

# tags_metadata = [
#     {"name": "Auth"},
#     {"name": "Users"},
#     {"name": "Products"},
# ]

# app = FastAPI(title="Final Project API", openapi_tags=tags_metadata)
app = FastAPI(title="Final Project API")

# Include our API routes
app.include_router(auth_router)
app.include_router(iol_router)
app.include_router(rava_router)
# # Let's include our auth routes aside from the API routes
# app.include_router(auth_router)


# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# uvicorn src.main:app --loop asyncio
