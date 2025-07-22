"""Response models for the solution guide generator API."""

from typing import Any

from pydantic import BaseModel, Field


class SolutionGuideResponse(BaseModel):
    """Response model for generated solution guides.

    Contains the generated markdown guide and metadata about
    the generation process.
    """

    guide: str = Field(
        ...,
        description="Generated solution guide in markdown format",
    )
    company_name: str = Field(
        ...,
        description="Company name the guide was generated for",
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="Additional metadata about the generation process",
    )


class ErrorResponse(BaseModel):
    """Error response model for API errors."""

    error: str = Field(
        ...,
        description="Error message",
    )
    detail: str | None = Field(
        None,
        description="Detailed error information",
    )
    code: str | None = Field(
        None,
        description="Error code for programmatic handling",
    )
