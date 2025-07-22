"""API routes for the solution guide generator."""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.requests import TranscriptRequest
from app.models.responses import SolutionGuideResponse
from app.services.guide_generator import GuideGenerator

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/api/v1", tags=["solution-guides"])


@router.post("/generate-guide", response_model=SolutionGuideResponse)
async def generate_solution_guide(request: TranscriptRequest):
    """Generate a solution guide from call transcript.

    This endpoint takes a call transcript, company name, and optional context
    to generate a customized technical solution guide using Glean's research
    capabilities and sophisticated prompt engineering.

    Args:
        request: TranscriptRequest containing transcript, company name, and context

    Returns:
        SolutionGuideResponse with the generated guide and metadata

    Raises:
        HTTPException: If the guide generation fails
    """
    try:
        logger.info(f"Received guide generation request for company: {request.company_name}")

        # Validate request
        if not request.transcript.strip():
            raise HTTPException(status_code=400, detail="Transcript cannot be empty")

        if not request.company_name.strip():
            raise HTTPException(status_code=400, detail="Company name cannot be empty")

        # Initialize the guide generator
        generator = GuideGenerator()

        # Generate the solution guide
        guide = await generator.generate_guide(
            transcript=request.transcript,
            company_name=request.company_name,
            additional_context=request.additional_context,
        )

        # Prepare response
        response = SolutionGuideResponse(
            guide=guide,
            company_name=request.company_name,
            metadata={
                "transcript_length": len(request.transcript),
                "has_additional_context": bool(request.additional_context),
                "generated_successfully": True,
            },
        )

        logger.info(f"Successfully generated guide for {request.company_name}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error generating guide for {request.company_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate solution guide: {str(e)}")


@router.post("/validate-environment")
async def validate_environment():
    """Validate that the application environment is properly configured.

    This endpoint checks the Glean API connectivity and configuration
    to ensure the application can function properly.

    Returns:
        Dictionary with validation results for different components
    """
    try:
        generator = GuideGenerator()
        validation = await generator.validate_environment()

        return {
            "valid": all(validation.values()),
            "details": validation,
            "message": "Environment validation completed",
        }

    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "valid": False,
                "details": {"error": str(e)},
                "message": "Environment validation failed",
            },
        )


@router.get("/health")
async def api_health_check():
    """Health check endpoint for the API router.

    Returns:
        Basic health status information
    """
    return {
        "status": "healthy",
        "service": "solution-guide-generator-api",
        "version": "0.1.0",
    }


@router.post("/research-company")
async def research_company(company_name: str):
    """Research a company using Glean APIs without generating a full guide.

    This endpoint can be used to test company research capabilities
    or to get company information for other purposes.

    Args:
        company_name: Name of the company to research

    Returns:
        Company research results from Glean
    """
    try:
        if not company_name.strip():
            raise HTTPException(status_code=400, detail="Company name cannot be empty")

        generator = GuideGenerator()
        insights = await generator._research_company(
            company_name=company_name,
            transcript="",  # Empty transcript for standalone research
            additional_context=None,
        )

        return {
            "company_name": company_name,
            "research_results": insights,
            "message": "Company research completed successfully",
        }

    except Exception as e:
        logger.error(f"Error researching company {company_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to research company: {str(e)}")
