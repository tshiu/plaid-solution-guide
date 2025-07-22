"""Request models for the solution guide generator API."""

from pydantic import BaseModel, Field


class TranscriptRequest(BaseModel):
    """Request model for generating solution guides from transcripts.

    This model validates and structures incoming requests to ensure
    all required data is present and properly formatted.
    """

    transcript: str = Field(
        ...,
        min_length=1,
        description="Call transcript content",
        example="TechCorp + Plaid Technical Demo\n\nParticipants...",
    )
    company_name: str = Field(
        ...,
        min_length=1,
        description="Target company name",
        example="TechCorp",
    )
    additional_context: str | None = Field(
        None,
        description="Extra context about the use case",
        example="They're building an HOA financial management platform",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "transcript": "Call transcript content here...",
                "company_name": "TechCorp Inc",
                "additional_context": "They're looking to implement payment processing",
            }
        }
    }
