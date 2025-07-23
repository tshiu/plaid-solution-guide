"""API routes for the solution guide generator."""

import logging
import time

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
    start_time = time.time()
    logger.info("🎯 SOLUTION GUIDE GENERATION REQUEST")
    logger.info(f"   Company: {request.company_name}")
    logger.info(f"   Transcript length: {len(request.transcript)} characters")
    logger.info(f"   Has additional context: {bool(request.additional_context)}")
    if request.additional_context:
        logger.info(f"   Additional context: {request.additional_context[:100]}...")

    try:
        # Validate request
        logger.info("🔍 Validating request data...")

        if not request.transcript.strip():
            logger.error("❌ Validation failed: Empty transcript")
            raise HTTPException(status_code=400, detail="Transcript cannot be empty")

        if not request.company_name.strip():
            logger.error("❌ Validation failed: Empty company name")
            raise HTTPException(status_code=400, detail="Company name cannot be empty")

        logger.info("✅ Request validation passed")

        # Initialize the guide generator
        logger.info("🏗️  Initializing guide generator...")
        generator = GuideGenerator()

        # Generate the solution guide
        logger.info("🚀 Starting guide generation process...")
        guide = await generator.generate_guide(
            transcript=request.transcript,
            company_name=request.company_name,
            additional_context=request.additional_context,
        )

        # Prepare response
        logger.info("📦 Preparing response...")
        response = SolutionGuideResponse(
            guide=guide,
            company_name=request.company_name,
            metadata={
                "transcript_length": len(request.transcript),
                "has_additional_context": bool(request.additional_context),
                "generated_successfully": True,
                "guide_length": len(guide),
                "processing_time": round(time.time() - start_time, 2),
            },
        )

        total_time = time.time() - start_time
        logger.info("🎉 SOLUTION GUIDE GENERATION SUCCESSFUL!")
        logger.info(f"   Company: {request.company_name}")
        logger.info(f"   Total processing time: {total_time:.2f}s")
        logger.info(f"   Generated guide length: {len(guide)} characters")

        return response

    except HTTPException as he:
        # Re-raise HTTP exceptions as-is but log them
        error_time = time.time() - start_time
        logger.error(f"❌ HTTP Exception after {error_time:.2f}s: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        error_time = time.time() - start_time
        logger.error("💥 SOLUTION GUIDE GENERATION FAILED!")
        logger.error(f"   Company: {request.company_name}")
        logger.error(f"   Time before failure: {error_time:.2f}s")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Error message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate solution guide: {str(e)}")


@router.post("/validate-environment")
async def validate_environment():
    """Validate that the application environment is properly configured.

    This endpoint checks the Glean API connectivity and configuration
    to ensure the application can function properly.

    Returns:
        Dictionary with validation results for different components
    """
    logger.info("🔧 ENVIRONMENT VALIDATION REQUEST")
    start_time = time.time()

    try:
        logger.info("   Creating guide generator for validation...")
        generator = GuideGenerator()

        logger.info("   Running validation checks...")
        validation = await generator.validate_environment()

        validation_time = time.time() - start_time

        all_valid = all(validation.values())
        logger.info(f"🔧 Environment validation completed in {validation_time:.2f}s")
        logger.info(f"   Overall result: {'✅ VALID' if all_valid else '❌ INVALID'}")

        for component, status in validation.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"   {component}: {status_icon} {status}")

        return {
            "valid": all_valid,
            "details": validation,
            "message": "Environment validation completed",
            "validation_time": round(validation_time, 2),
        }

    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"💥 Environment validation failed after {error_time:.2f}s:")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Error message: {str(e)}")

        return JSONResponse(
            status_code=500,
            content={
                "valid": False,
                "details": {"error": str(e)},
                "message": "Environment validation failed",
                "validation_time": round(error_time, 2),
            },
        )


@router.get("/health")
async def api_health_check():
    """Health check endpoint for the API router.

    Returns:
        Basic health status information
    """
    logger.info("❤️  API health check requested")

    health_response = {
        "status": "healthy",
        "service": "solution-guide-generator-api",
        "version": "0.1.0",
    }

    logger.info(f"❤️  API health check: {health_response['status']}")
    return health_response


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
    start_time = time.time()
    logger.info("🔍 COMPANY RESEARCH REQUEST")
    logger.info(f"   Company: {company_name}")

    try:
        # Validate input
        if not company_name.strip():
            logger.error("❌ Validation failed: Empty company name")
            raise HTTPException(status_code=400, detail="Company name cannot be empty")

        logger.info("✅ Request validation passed")

        # Initialize generator and research company
        logger.info("🏗️  Creating guide generator for research...")
        generator = GuideGenerator()

        logger.info("🔬 Starting company research...")
        insights = await generator._research_company(
            company_name=company_name,
            transcript="",  # Empty transcript for standalone research
            additional_context=None,
        )

        research_time = time.time() - start_time

        if "error" in insights:
            logger.warning(f"⚠️  Research completed with issues in {research_time:.2f}s")
            logger.warning(f"   Error: {insights['error']}")
        else:
            logger.info(f"🎉 Company research successful in {research_time:.2f}s")
            logger.info(f"   Company: {company_name}")

        return {
            "company_name": company_name,
            "research_results": insights,
            "message": "Company research completed successfully",
            "research_time": round(research_time, 2),
        }

    except HTTPException as he:
        # Re-raise HTTP exceptions as-is but log them
        error_time = time.time() - start_time
        logger.error(f"❌ HTTP Exception after {error_time:.2f}s: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        error_time = time.time() - start_time
        logger.error("💥 COMPANY RESEARCH FAILED!")
        logger.error(f"   Company: {company_name}")
        logger.error(f"   Time before failure: {error_time:.2f}s")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Error message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to research company: {str(e)}")
