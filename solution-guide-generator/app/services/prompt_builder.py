"""Prompt builder for generating solution guides using LLM."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds sophisticated prompts for generating solution guides.

    This class creates structured prompts that guide the LLM to generate
    technical solution guides in the style of the successful IntelXLabs example.
    """

    def __init__(self):
        """Initialize the prompt builder with templates."""
        self.intelxlabs_example = self._load_intelxlabs_example()

    def _load_intelxlabs_example(self) -> str:
        """Load the IntelXLabs guide example as a reference template."""
        return """
# IntelXLabs + Plaid // Solutions Guide

## What You're Building

HOA financial management platform that needs to:
- Connect bank accounts for business customers (HOAs)
- Import transaction data for accounting/reconciliation
- Integrate with Stripe for payments
- Keep sensitive data storage minimal for compliance

## Core Plaid Integration

### 1. Bank Account Connection (`Link` + `Auth`)
**What it does**: Secure bank account linking with account/routing number retrieval

**Customization**: Logo, colors, copy via dashboard templates

### 2. Stripe Integration (`Auth`)
**One extra API call** after account connection

### 3. Transaction Data (`Transactions`)
**Real-time transaction sync** for accounting features

## Key Technical Details

### Access Token Management
- **Tokens don't expire** (unless user changes bank password)
- Store encrypted in your backend only
- Get webhooks when tokens need updates
- Users can revoke via `/item/remove` endpoint

### Implementation Flow
1. HOA user clicks "Connect Bank Account"
2. Plaid Link opens (with your branding)
3. User authenticates with their bank
4. You get access_token
5. Generate Stripe processor token
6. Start syncing transaction data

## What You Get Out of the Box
✅ **Security**: SOC 2, PCI DSS, GDPR compliant
✅ **Bank Coverage**: 12,000+ US institutions
✅ **Webhooks**: Real-time account status updates
✅ **User Control**: Built-in consent and revocation

## Answers to Your Questions
[Table format with specific Q&A from the call]

## Getting Started
1. **Sandbox**: Test with fake banks
2. **Limited Production**: Real banks, capped API calls
3. **Production**: Full access after commercial agreement
"""

    def build_solution_guide_prompt(
        self,
        transcript: str,
        company_name: str,
        company_research: dict[str, Any],
        additional_context: str | None = None,
    ) -> str:
        """Build a comprehensive prompt for generating solution guides.

        Args:
            transcript: Call transcript content
            company_name: Target company name
            company_research: Research data from Glean
            additional_context: Optional additional context

        Returns:
            Formatted prompt string for LLM generation
        """

        # Extract relevant information from company research
        business_overview = company_research.get("business_overview", "No business overview available")
        technical_context = company_research.get("technical_context", "No technical context available")

        prompt = f"""You are an expert sales engineer creating technical solution guides for Plaid's financial APIs.

Your task is to analyze this call transcript from {company_name} and generate a concise, technical solution guide \
that matches the style and format of the example provided.

## CALL TRANSCRIPT:
{transcript}

## COMPANY RESEARCH:
### Business Overview:
{business_overview}

### Technical Context:
{technical_context}

## ADDITIONAL CONTEXT:
{additional_context or "No additional context provided"}

## EXAMPLE SOLUTION GUIDE STYLE:
{self.intelxlabs_example}

## INSTRUCTIONS:
Generate a solution guide for {company_name} that follows these principles:

1. **Focus on technical implementation** - Include specific API calls, code examples, and integration flows
2. **Avoid business jargon** - Write for technical PMs who need actionable information
3. **Use clear, scannable formatting** - Tables, bullet points, code blocks, checkboxes
4. **Address specific questions** - Extract and answer questions raised in the call transcript
5. **Provide actionable next steps** - Clear implementation roadmap
6. **Match the tone and structure** - Concise, practical, technically focused like the example

## KEY REQUIREMENTS:
- Title format: "{company_name} + Plaid // Solutions Guide"
- Start with "What You're Building" section describing their specific use case
- Include "Core Integration" section with specific Plaid products needed
- Add "Key Technical Details" with implementation specifics
- Include "What You Get Out of the Box" with relevant benefits
- Create "Answers to Your Questions" section addressing call discussion points
- End with "Getting Started" steps

## OUTPUT:
Generate the complete solution guide for {company_name} now, following the exact style and structure of the example:"""

        return prompt

    def build_company_research_prompt(self, company_name: str, transcript_excerpt: str) -> str:
        """Build a prompt for researching company information.

        Args:
            company_name: Name of the company to research
            transcript_excerpt: Key excerpt from the transcript for context

        Returns:
            Research prompt for Glean chat
        """
        return f"""Based on this call transcript excerpt from {company_name}, help me understand their business \
and technical requirements:

TRANSCRIPT EXCERPT:
{transcript_excerpt}

Please provide:
1. What industry/sector is {company_name} in?
2. What is their business model and primary products/services?
3. What technical challenges might they face?
4. What integration requirements should we consider?
5. Who are their likely customers/users?

Focus on information that would help create a targeted technical solution guide."""
