"""
Test suite for Smart Correction Service.
"""
import pytest
import os
from unittest.mock import Mock, patch
from backend.services.smart_correction_service import SmartCorrectionService


class TestSmartCorrectionService:
    """Test cases for SmartCorrectionService."""
    
    @pytest.fixture
    def mock_gemini_response(self):
        """Create a mock Gemini response."""
        def _create_response(is_misspelled, corrected_name, ticker, confidence):
            mock_response = Mock()
            mock_response.text = f'''```json
{{
    "is_misspelled": {str(is_misspelled).lower()},
    "original_input": "test input",
    "corrected_name": "{corrected_name}",
    "ticker": "{ticker}",
    "confidence": "{confidence}",
    "explanation": "Test explanation"
}}
```'''
            return mock_response
        return _create_response
    
    @pytest.fixture
    def service(self):
        """Create a SmartCorrectionService instance."""
        # Mock the API key
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel'):
                    service = SmartCorrectionService(api_key='test_key')
                    return service
    
    def test_detect_simple_typo(self, service, mock_gemini_response):
        """Test detection of simple typo (matae -> Meta)."""
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_generate.return_value = mock_gemini_response(
                True, "Meta Platforms Inc.", "META", "high"
            )
            
            result = service.detect_and_correct("matae")
            
            assert result['is_misspelled'] == True
            assert result['corrected_name'] == "Meta Platforms Inc."
            assert result['ticker'] == "META"
            assert result['confidence'] == "high"
    
    def test_detect_phonetic_similarity(self, service, mock_gemini_response):
        """Test detection of phonetic similarity (microsft -> Microsoft)."""
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_generate.return_value = mock_gemini_response(
                True, "Microsoft Corporation", "MSFT", "high"
            )
            
            result = service.detect_and_correct("microsft")
            
            assert result['is_misspelled'] == True
            assert result['corrected_name'] == "Microsoft Corporation"
            assert result['ticker'] == "MSFT"
    
    def test_correct_spelling_no_correction(self, service, mock_gemini_response):
        """Test that correctly spelled names don't trigger correction."""
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = '''```json
{
    "is_misspelled": false,
    "original_input": "Apple",
    "corrected_name": null,
    "ticker": null,
    "confidence": "high",
    "explanation": "Correctly spelled company name"
}
```'''
            mock_generate.return_value = mock_response
            
            result = service.detect_and_correct("Apple")
            
            assert result['is_misspelled'] == False
            assert result['corrected_name'] is None
    
    def test_valid_ticker_no_correction(self, service, mock_gemini_response):
        """Test that valid tickers don't trigger correction."""
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = '''```json
{
    "is_misspelled": false,
    "original_input": "AAPL",
    "corrected_name": null,
    "ticker": null,
    "confidence": "high",
    "explanation": "Valid ticker symbol"
}
```'''
            mock_generate.return_value = mock_response
            
            result = service.detect_and_correct("AAPL")
            
            assert result['is_misspelled'] == False
    
    def test_multiple_typos_in_query(self, service, mock_gemini_response):
        """Test detection in a full query with typos."""
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_generate.return_value = mock_gemini_response(
                True, "Meta Platforms Inc.", "META", "high"
            )
            
            result = service.detect_and_correct("analyze matae for 1 month")
            
            assert result['is_misspelled'] == True
            assert result['ticker'] == "META"
    
    def test_generate_confirmation_message_high_confidence(self, service):
        """Test confirmation message generation with high confidence."""
        correction_result = {
            'is_misspelled': True,
            'corrected_name': 'Meta Platforms Inc.',
            'ticker': 'META',
            'confidence': 'high'
        }
        
        message = service.generate_confirmation_message(correction_result)
        
        assert message is not None
        assert "Meta Platforms Inc." in message
        assert "META" in message
        assert "Did you mean" in message
    
    def test_generate_confirmation_message_medium_confidence(self, service):
        """Test confirmation message generation with medium confidence."""
        correction_result = {
            'is_misspelled': True,
            'corrected_name': 'Tesla Inc.',
            'ticker': 'TSLA',
            'confidence': 'medium'
        }
        
        message = service.generate_confirmation_message(correction_result)
        
        assert message is not None
        assert "moderately confident" in message.lower()
    
    def test_generate_confirmation_message_low_confidence(self, service):
        """Test confirmation message generation with low confidence."""
        correction_result = {
            'is_misspelled': True,
            'corrected_name': 'Unknown Corp',
            'ticker': 'UNK',
            'confidence': 'low'
        }
        
        message = service.generate_confirmation_message(correction_result)
        
        assert message is not None
        assert "not very confident" in message.lower()
    
    def test_no_confirmation_message_when_not_misspelled(self, service):
        """Test that no confirmation message is generated when not misspelled."""
        correction_result = {
            'is_misspelled': False,
            'corrected_name': None,
            'ticker': None,
            'confidence': 'high'
        }
        
        message = service.generate_confirmation_message(correction_result)
        
        assert message is None
    
    def test_error_handling(self, service):
        """Test error handling when Gemini API fails."""
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            
            result = service.detect_and_correct("test input")
            
            # Should return safe fallback
            assert result['is_misspelled'] == False
            assert result['confidence'] == 'low'
            assert 'error' in result['explanation'].lower()
    
    def test_json_extraction_with_markdown(self, service):
        """Test JSON extraction from markdown code blocks."""
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = '''Here is the result:
```json
{
    "is_misspelled": true,
    "original_input": "gogle",
    "corrected_name": "Alphabet Inc.",
    "ticker": "GOOGL",
    "confidence": "high",
    "explanation": "Common typo"
}
```
Hope this helps!'''
            mock_generate.return_value = mock_response
            
            result = service.detect_and_correct("gogle")
            
            assert result['is_misspelled'] == True
            assert result['ticker'] == "GOOGL"
    
    def test_json_extraction_without_markdown(self, service):
        """Test JSON extraction from plain text."""
        with patch.object(service.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = '''{
    "is_misspelled": true,
    "original_input": "amazn",
    "corrected_name": "Amazon.com Inc.",
    "ticker": "AMZN",
    "confidence": "high",
    "explanation": "Missing 'o'"
}'''
            mock_generate.return_value = mock_response
            
            result = service.detect_and_correct("amazn")
            
            assert result['is_misspelled'] == True
            assert result['ticker'] == "AMZN"


class TestSmartCorrectionIntegration:
    """Integration tests for smart correction with real scenarios."""
    
    def test_common_typos(self):
        """Test common typo scenarios."""
        test_cases = [
            ("matae", "META"),
            ("metae", "META"),
            ("microsft", "MSFT"),
            ("gogle", "GOOGL"),
            ("amazn", "AMZN"),
            ("tesle", "TSLA"),
            ("nvidea", "NVDA"),
        ]
        
        # These would require actual API calls in a real integration test
        # For now, we're documenting expected behavior
        for input_text, expected_ticker in test_cases:
            # In real test: result = service.detect_and_correct(input_text)
            # assert result['ticker'] == expected_ticker
            pass
    
    def test_correctly_spelled_names(self):
        """Test that correctly spelled names are not corrected."""
        test_cases = [
            "Apple",
            "Microsoft",
            "Google",
            "Amazon",
            "Tesla",
            "Meta",
        ]
        
        # These should return is_misspelled=False
        for input_text in test_cases:
            # In real test: result = service.detect_and_correct(input_text)
            # assert result['is_misspelled'] == False
            pass
    
    def test_valid_tickers(self):
        """Test that valid tickers are not corrected."""
        test_cases = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
        ]
        
        # These should return is_misspelled=False
        for input_text in test_cases:
            # In real test: result = service.detect_and_correct(input_text)
            # assert result['is_misspelled'] == False
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

