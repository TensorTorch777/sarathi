"""Aggregate v1 API routers."""

from fastapi import APIRouter

from app.api.v1.routers import auth, chat, health, memory, retrieval, users, version, voice

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(version.router, tags=["version"])
api_v1_router.include_router(auth.router, tags=["auth"])
api_v1_router.include_router(users.router, tags=["users"])
api_v1_router.include_router(retrieval.router, tags=["retrieval"])
api_v1_router.include_router(chat.router, tags=["chat"])
api_v1_router.include_router(voice.router, tags=["voice"])
api_v1_router.include_router(memory.router, tags=["memory"])
