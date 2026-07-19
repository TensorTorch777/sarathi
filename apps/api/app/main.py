"""FastAPI application entrypoint for Sarathi AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.lifespan import lifespan
from app.api.v1 import api_v1_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.middleware import RequestContextMiddleware


def create_app() -> FastAPI:
    """Application factory — wires middleware, handlers, and routers."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.app_debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_v1_router, prefix=settings.api_prefix)

    return app


app = create_app()
