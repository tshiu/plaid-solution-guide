"""Prompt builder for generating solution guides using LLM."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds sophisticated prompts for generating solution guides.

    This class creates structured prompts that guide the LLM to generate
    technical solution guides using established templates and patterns.
    """

    def __init__(self):
        """Initialize the prompt builder with templates."""
        logger.info("📝 Initializing Prompt Builder...")
        self.template_example = self._load_template_example()
        logger.info("✅ Prompt Builder initialized with template example")

    def _load_template_example(self) -> str:
        """Load the guide template as a reference example."""
        logger.info("📋 Loading template example for prompt building...")

        template = """
# CompanyName + Plaid // Solutions Guide

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

**Documentation**: [Link Overview](https://plaid.com/docs/link/) | [Auth API](https://plaid.com/docs/auth/)

### 2. Stripe Integration (`Auth`)
**One extra API call** after account connection

### 3. Transaction Data (`Transactions`)
**Real-time transaction sync** for accounting features

**Documentation**: [Transactions API](https://plaid.com/docs/transactions/)

## Integration Flow

```mermaid
sequenceDiagram
    participant User as HOA User
    participant App as Your App
    participant Plaid as Plaid Link
    participant Bank as User's Bank
    participant Stripe as Stripe

    User->>App: Click "Connect Bank Account"
    App->>Plaid: Initialize Link Token
    Plaid-->>App: Link Token
    App->>User: Show Plaid Link UI
    User->>Plaid: Enter bank credentials
    Plaid->>Bank: Authenticate user
    Bank-->>Plaid: Auth success
    Plaid-->>App: public_token
    App->>Plaid: Exchange for access_token
    Plaid-->>App: access_token & account info
    App->>Plaid: Get Auth data (account/routing)
    Plaid-->>App: Account details
    App->>Stripe: Create processor token
    Stripe-->>App: Processor token
    App->>Plaid: Start transaction sync
    Plaid-->>App: Transaction data
```

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

## Documentation & Resources

### Core API Documentation
- **[Plaid Link](https://plaid.com/docs/link/)** - Client-side account connection flow
- **[Auth API](https://plaid.com/docs/auth/)** - Account/routing numbers for ACH and payments
- **[Transactions API](https://plaid.com/docs/transactions/)** - Real-time transaction data access
- **[Identity API](https://plaid.com/docs/identity/)** - Account holder verification
- **[Assets API](https://plaid.com/docs/assets/)** - Comprehensive financial reports

### Developer Tools & Resources
- **[API Reference](https://plaid.com/docs/api/)** - Complete endpoint documentation
- **[Quickstart Guide](https://plaid.com/docs/quickstart/)** - Get started in minutes
- **[Postman Collection](https://plaid.com/docs/developer-tools/postman/)** - Test APIs easily

### Support & Community
- **[Developer Support](https://plaid.com/docs/resources/)** - Technical support resources

## Getting Started
1. **Sandbox**: Test with fake banks using [Quickstart Guide](https://plaid.com/docs/quickstart/)
2. **Limited Production**: Real banks, capped API calls
3. **Production**: Full access after commercial agreement
"""

        logger.info(f"✅ Template example loaded: {len(template)} characters")
        return template

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
        logger.info("🏗️  Building solution guide prompt...")
        logger.info(f"   Company: {company_name}")
        logger.info(f"   Transcript length: {len(transcript)} characters")
        logger.info(f"   Has additional context: {bool(additional_context)}")

        # Extract relevant information from company research
        logger.info("📊 Extracting information from company research...")
        business_overview = company_research.get("business_overview", "No business overview available")
        technical_context = company_research.get("technical_context", "No technical context available")

        has_business_overview = business_overview != "No business overview available"
        has_technical_context = technical_context != "No technical context available"

        logger.info(f"   Business overview available: {has_business_overview}")
        logger.info(f"   Technical context available: {has_technical_context}")

        if has_business_overview:
            logger.info(f"   Business overview length: {len(business_overview)} characters")
        if has_technical_context:
            logger.info(f"   Technical context length: {len(technical_context)} characters")

        logger.info("📝 Constructing comprehensive prompt...")
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
        {self.template_example}

## INSTRUCTIONS:
Generate a solution guide for {company_name} that follows these principles:

1. **Focus on technical implementation** - Include specific API calls, code examples, and integration flows
2. **Avoid business jargon** - Write for technical PMs who need actionable information
3. **Use clear, scannable formatting** - Tables, bullet points, code blocks, checkboxes
4. **Address specific questions** - Extract and answer questions raised in the call transcript
5. **Provide actionable next steps** - Clear implementation roadmap
6. **Match the tone and structure** - Concise, practical, technically focused like the example
7. **Include sequence diagrams** - Add a Mermaid sequence diagram showing the integration flow
8. **Include relevant documentation links** - Add links to Plaid's developer documentation throughout

## KEY REQUIREMENTS:
- Title format: "{company_name} + Plaid // Solutions Guide"
- Start with "What You're Building" section describing their specific use case
- Include "Core Integration" section with specific Plaid products needed
- **MANDATORY**: Add "Integration Flow" section with a Mermaid sequence diagram showing the step-by-step process
- Add "Key Technical Details" with implementation specifics
- Include "What You Get Out of the Box" with relevant benefits
- Create "Answers to Your Questions" section addressing call discussion points
- **MANDATORY**: Include "Documentation & Resources" section with relevant Plaid documentation links
- End with "Getting Started" steps

## PLAID DOCUMENTATION LINKS TO INCLUDE:
Use these official Plaid documentation URLs where relevant:

### Core API Documentation:
- **Plaid Link**: https://plaid.com/docs/link/ (account connection flow)
- **Auth API**: https://plaid.com/docs/auth/ (account/routing numbers for ACH)
- **Transactions API**: https://plaid.com/docs/transactions/ (transaction data access)
- **Identity API**: https://plaid.com/docs/identity/ (account holder verification)
- **Assets API**: https://plaid.com/docs/assets/ (comprehensive financial reports)

### Developer Resources:
- **API Reference**: https://plaid.com/docs/api/ (complete endpoint documentation)
- **Quickstart Guide**: https://plaid.com/docs/quickstart/ (getting started tutorial)
- **Postman Collection**: https://plaid.com/docs/developer-tools/postman/ (API testing tools)
- **Developer Support**: https://plaid.com/docs/resources/ (technical support resources)

## DOCUMENTATION INTEGRATION REQUIREMENTS:
1. **In Core Integration section**: Add documentation links for each Plaid product mentioned
2. **In Key Technical Details**: Link to relevant API references and guides
3. **In Getting Started**: Include link to Quickstart Guide for sandbox setup
4. **Create comprehensive Documentation & Resources section** with:
   - Core API Documentation subsection
   - Developer Tools & Resources subsection  
   - Support & Community subsection
5. **Throughout the guide**: Add inline links where specific APIs or features are mentioned

## SEQUENCE DIAGRAM REQUIREMENTS:
- Use Mermaid syntax: ```mermaid sequenceDiagram ... ```
- Include key participants: User, Your App, Plaid, Bank, and any third-party services mentioned
- Show the complete flow from user action to final result
- Include API calls, token exchanges, and data flows
- Make it specific to {company_name}'s use case and requirements

## OUTPUT:
Generate the complete solution guide for {company_name} now, following the exact style and structure of the example:"""

        logger.info(f"✅ Solution guide prompt constructed: {len(prompt)} characters")
        logger.info("   Prompt includes:")
        logger.info("     ✓ Call transcript")
        logger.info("     ✓ Company research data")
        logger.info("     ✓ Template example")
        logger.info("     ✓ Detailed instructions")
        logger.info("     ✓ Output requirements")

        return prompt

    def build_company_research_prompt(self, company_name: str, transcript_excerpt: str) -> str:
        """Build a prompt for researching company information.

        Args:
            company_name: Name of the company to research
            transcript_excerpt: Key excerpt from the transcript for context

        Returns:
            Research prompt for Glean chat
        """
        logger.info(f"🔍 Building company research prompt for '{company_name}'...")
        logger.info(f"   Transcript excerpt length: {len(transcript_excerpt)} characters")

        research_prompt = f"""Based on this call transcript from {company_name}, help me understand their business
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

        logger.info(f"✅ Company research prompt built: {len(research_prompt)} characters")
        logger.info("   Research prompt will ask about:")
        logger.info("     • Industry/sector")
        logger.info("     • Business model")
        logger.info("     • Technical challenges")
        logger.info("     • Integration requirements")
        logger.info("     • Customer base")

        return research_prompt
