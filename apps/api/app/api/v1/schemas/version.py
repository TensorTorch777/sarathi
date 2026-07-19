"""Version endpoint schemas."""

from pydantic import BaseModel, Field


class VersionResponse(BaseModel):
    """HTTP response for application version metadata."""

    name: str = Field(description="Application name")
    version: str = Field(description="Application semantic version")
    environment: str = Field(description="Deployment environment")
    api: str = Field(description="API version label", default="v1")
