#!/usr/bin/env python3
"""
Manual test script for Smart Correction Service.
This script makes real API calls to test the smart correction functionality.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.smart_correction_service import SmartCorrectionService
import structlog

# Configure logging
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging_level=20),
)

logger = structlog.get_logger()


def test_correction(service: SmartCorrectionService, test_input: str):
    """Test a single correction."""
    print(f"\n{'='*80}")
    print(f"Testing: '{test_input}'")
    print(f"{'='*80}")
    
    try:
        result = service.detect_and_correct(test_input)
        
        print(f"\n📊 Result:")
        print(f"  Is Misspelled: {result.get('is_misspelled')}")
        print(f"  Original Input: {result.get('original_input')}")
        print(f"  Corrected Name: {result.get('corrected_name')}")
        print(f"  Ticker: {result.get('ticker')}")
        print(f"  Confidence: {result.get('confidence')}")
        print(f"  Explanation: {result.get('explanation')}")
        
        if result.get('is_misspelled'):
            message = service.generate_confirmation_message(result)
            print(f"\n💬 Confirmation Message:")
            print(f"  {message}")
        else:
            print(f"\n✅ No correction needed")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None


def main():
    """Run manual tests."""
    print("🚀 Smart Correction Service - Manual Test Suite")
    print("=" * 80)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        print("Please set GEMINI_API_KEY before running this script")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Initialize service
    try:
        service = SmartCorrectionService(api_key=api_key)
        print("✅ SmartCorrectionService initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize service: {str(e)}")
        sys.exit(1)
    
    # Test cases
    test_cases = [
        # Simple typos
        ("matae", "Should detect as Meta (META)"),
        ("metae", "Should detect as Meta (META)"),
        ("microsft", "Should detect as Microsoft (MSFT)"),
        ("gogle", "Should detect as Google/Alphabet (GOOGL)"),
        ("amazn", "Should detect as Amazon (AMZN)"),
        ("tesle", "Should detect as Tesla (TSLA)"),
        ("nvidea", "Should detect as Nvidia (NVDA)"),
        
        # Correctly spelled
        ("Apple", "Should NOT correct - correctly spelled"),
        ("Microsoft", "Should NOT correct - correctly spelled"),
        ("Meta", "Should NOT correct - correctly spelled"),
        
        # Valid tickers
        ("AAPL", "Should NOT correct - valid ticker"),
        ("MSFT", "Should NOT correct - valid ticker"),
        ("META", "Should NOT correct - valid ticker"),
        
        # Full queries
        ("analyze matae for 1 month", "Should detect Meta in full query"),
        ("compare microsft and gogle", "Should detect Microsoft in full query"),
        ("Analyze NVDA and AMD", "Should NOT correct - valid tickers"),
    ]
    
    print(f"\n📝 Running {len(test_cases)} test cases...\n")
    
    results = []
    for test_input, description in test_cases:
        print(f"\n{'─'*80}")
        print(f"📌 {description}")
        result = test_correction(service, test_input)
        results.append((test_input, description, result))
    
    # Summary
    print(f"\n\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    total = len(results)
    successful = sum(1 for _, _, r in results if r is not None)
    misspelled = sum(1 for _, _, r in results if r and r.get('is_misspelled'))
    correct = sum(1 for _, _, r in results if r and not r.get('is_misspelled'))
    
    print(f"\nTotal Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Misspellings Detected: {misspelled}")
    print(f"Correct Inputs: {correct}")
    
    print(f"\n{'='*80}")
    print("✅ Testing complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

