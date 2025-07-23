#!/usr/bin/env python3
"""Integration tests for real API responses.

This script tests the actual Glean API integration without mocks.
Run this script to verify that the real API calls work correctly.

Usage:
    python scripts/integration_test.py
    OR
    uv run python scripts/integration_test.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.glean_client import GleanClient
from app.services.guide_generator import GuideGenerator


async def test_glean_client_integration():
    """Test the Glean client with real API calls."""
    print("🔧 Testing Glean Client Integration")
    print("=" * 50)

    client = GleanClient()

    # Test 1: Company Search
    print("\n📊 Test 1: Company Search")
    start_time = time.time()

    try:
        result = await client.search_company("Stripe")
        duration = time.time() - start_time

        if result.get("error"):
            print(f"❌ Search failed: {result['error']}")
            return False
        else:
            print(f"✅ Search successful in {duration:.2f}s")
            print(f"   Found {len(result.get('results', []))} results")
            if result.get("results"):
                first_result = result["results"][0]
                print(f"   First result: {first_result.get('title', 'No title')}")
                print(f"   URL: {first_result.get('url', 'No URL')}")
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

    # Test 2: Simple Chat Query
    print("\n💬 Test 2: Simple Chat Query")
    start_time = time.time()

    try:
        chat_result = await client.chat_query("What is Plaid in one sentence?")
        duration = time.time() - start_time

        if "failed" in chat_result.lower():
            print(f"❌ Chat failed: {chat_result}")
            return False
        else:
            print(f"✅ Chat successful in {duration:.2f}s")
            print(f"   Response length: {len(chat_result)} characters")
            print(f"   Preview: {chat_result[:150]}...")
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

    # Test 3: Chat with Context
    print("\n🔗 Test 3: Chat with Context")
    start_time = time.time()

    try:
        context = ["We are evaluating payment processors.", "Cost and security are our main concerns."]
        chat_with_context = await client.chat_query("How does Plaid help with payment security?", context)
        duration = time.time() - start_time

        if "failed" in chat_with_context.lower():
            print(f"❌ Context chat failed: {chat_with_context}")
            return False
        else:
            print(f"✅ Context chat successful in {duration:.2f}s")
            print(f"   Response length: {len(chat_with_context)} characters")
            print(f"   Preview: {chat_with_context[:150]}...")
    except Exception as e:
        print(f"❌ Context chat error: {e}")
        return False

    # Test 4: Company Insights
    print("\n🔍 Test 4: Company Insights")
    start_time = time.time()

    try:
        insights = await client.get_company_insights("Square", "payment processing")
        duration = time.time() - start_time

        if insights.get("search_results", {}).get("error"):
            print(f"❌ Insights failed: {insights['search_results']['error']}")
            return False
        else:
            print(f"✅ Insights successful in {duration:.2f}s")
            print(f"   Search results: {insights['search_results']['total_results']} items")
            print(f"   Business overview: {len(insights.get('business_overview', ''))} chars")
            print(f"   Technical context: {len(insights.get('technical_context', ''))} chars")

            if insights.get("business_overview") and "failed" not in insights["business_overview"].lower():
                print(f"   Business preview: {insights['business_overview'][:100]}...")
    except Exception as e:
        print(f"❌ Insights error: {e}")
        return False

    print("\n✅ All Glean client tests passed!")
    return True


async def test_guide_generator_integration():
    """Test the guide generator with real API calls."""
    print("\n🚀 Testing Guide Generator Integration")
    print("=" * 50)

    generator = GuideGenerator()

    # Test 1: Environment Validation
    print("\n🔧 Test 1: Environment Validation")
    start_time = time.time()

    try:
        validation = await generator.validate_environment()
        duration = time.time() - start_time

        all_valid = all(validation.values())
        if all_valid:
            print(f"✅ Environment validation passed in {duration:.2f}s")
            for component, status in validation.items():
                print(f"   {component}: {'✅' if status else '❌'}")
        else:
            print(f"⚠️  Environment validation partial failure in {duration:.2f}s")
            for component, status in validation.items():
                print(f"   {component}: {'✅' if status else '❌'}")
    except Exception as e:
        print(f"❌ Environment validation error: {e}")
        return False

    # Test 2: Company Research
    print("\n📊 Test 2: Company Research")
    start_time = time.time()

    try:
        research = await generator._research_company(
            company_name="Stripe",
            transcript="Sample transcript mentioning payment processing",
            additional_context="They need secure payment integration",
        )
        duration = time.time() - start_time

        if research.get("error"):
            print(f"❌ Research failed: {research['error']}")
            return False
        else:
            print(f"✅ Research successful in {duration:.2f}s")
            print(f"   Company: {research.get('company_name', 'Unknown')}")
            print(f"   Business overview length: {len(research.get('business_overview', ''))}")
            if research.get("business_overview"):
                print(f"   Business preview: {research['business_overview'][:100]}...")
    except Exception as e:
        print(f"❌ Research error: {e}")
        return False

    # Test 3: Small Guide Generation (to avoid long API calls)
    print("\n📝 Test 3: Guide Generation (Short)")
    start_time = time.time()

    try:
        short_transcript = """
        Tech Startup + Plaid Demo Call

        Participants:
        - Sarah (Tech Startup CTO)
        - Alex (Plaid Solutions Engineer)

        Call Summary:
        Sarah's fintech startup needs secure bank account linking.
        Alex demonstrated Plaid's Link component and Auth API.
        Sarah is interested in identity verification features.
        """

        guide = await generator.generate_guide(
            transcript=short_transcript,
            company_name="Tech Startup",
            additional_context="Early-stage fintech focused on consumer banking",
        )
        duration = time.time() - start_time

        if not guide or "error" in guide.lower():
            print(f"❌ Guide generation failed: {guide[:100] if guide else 'No guide returned'}...")
            return False
        else:
            print(f"✅ Guide generation successful in {duration:.2f}s")
            print(f"   Guide length: {len(guide)} characters")
            print(f"   Preview:\n{guide[:300]}...")
    except Exception as e:
        print(f"❌ Guide generation error: {e}")
        return False

    print("\n✅ All guide generator tests passed!")
    return True


async def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\n🛡️  Testing Error Handling")
    print("=" * 30)

    client = GleanClient()

    # Test with non-existent company
    print("\n🔍 Test: Non-existent Company Search")
    try:
        result = await client.search_company("NonExistentCompanyXYZ123")
        # Should not fail, just return empty results
        print(f"✅ Handled gracefully: {len(result.get('results', []))} results")
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")

    # Test with empty query
    print("\n💬 Test: Empty Chat Query")
    try:
        result = await client.chat_query("")
        if "failed" in result.lower() or not result.strip():
            print("✅ Empty query handled appropriately")
        else:
            print(f"⚠️  Unexpected response: {result[:50]}...")
    except Exception as e:
        print(f"✅ Error handling working: {type(e).__name__}")

    print("\n✅ Error handling tests completed!")
    return True


async def main():
    """Run all integration tests."""
    print("🧪 INTEGRATION TESTS - Real API Responses")
    print("=" * 60)
    print("This script tests actual API calls to verify integration.")
    print("Make sure your .env file has valid Glean credentials.")
    print()

    start_total = time.time()

    # Run all test suites
    results = []

    try:
        results.append(await test_glean_client_integration())
        results.append(await test_guide_generator_integration())
        results.append(await test_error_handling())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        return

    total_duration = time.time() - start_total

    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total} test suites")
    print(f"⏱️  Total time: {total_duration:.2f} seconds")

    if all(results):
        print("🎉 All integration tests passed!")
        print("\n🚀 The application is ready for production use!")
    else:
        print("⚠️  Some tests failed. Check the logs above.")
        print("\n🔧 Review your configuration and try again.")


if __name__ == "__main__":
    # Run the integration tests
    asyncio.run(main())
