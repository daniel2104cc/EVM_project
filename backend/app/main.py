from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="EVM Project Dashboard API",
    description="REST API for project management and Earned Value Management analysis.",
    version="0.1.0",
    docs_url="/api-docs",
)

app.include_router(api_router, prefix="/api")
