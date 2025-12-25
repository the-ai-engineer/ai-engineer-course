"""FastAPI application for HR Policy Agent."""

from fastapi import FastAPI

from app.api import router

app = FastAPI(
    title="HR Policy Agent API",
    description="AI-powered HR policy assistant with document search",
    version="1.0.0",
)

app.include_router(router)
