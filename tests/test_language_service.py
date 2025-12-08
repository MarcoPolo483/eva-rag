"""Tests for language detection service."""
from eva_rag.services.language_service import LanguageDetectionService


def test_language_detection_english() -> None:
    """Test language detection identifies English."""
    service = LanguageDetectionService()
    
    text = "This is an English document. It contains multiple sentences for testing."
    language = service.detect_language(text)
    
    assert language == "en"


def test_language_detection_french() -> None:
    """Test language detection identifies French."""
    service = LanguageDetectionService()
    
    text = "Ceci est un document français. Il contient plusieurs phrases pour les tests."
    language = service.detect_language(text)
    
    assert language == "fr"


def test_language_detection_short_text() -> None:
    """Test language detection defaults to English for short text."""
    service = LanguageDetectionService()
    
    text = "Hi"
    language = service.detect_language(text)
    
    assert language == "en"


def test_language_detection_empty_text() -> None:
    """Test language detection defaults to English for empty text."""
    service = LanguageDetectionService()
    
    language = service.detect_language("")
    
    assert language == "en"


def test_language_detection_unsupported_language() -> None:
    """Test language detection defaults to English for unsupported languages."""
    service = LanguageDetectionService()
    
    # Spanish text (not in supported_languages)
    text = "Este es un documento en español. Contiene varias oraciones para pruebas."
    language = service.detect_language(text)
    
    # Should default to English since Spanish is not supported
    assert language == "en"


def test_is_supported_english() -> None:
    """Test is_supported returns True for English."""
    service = LanguageDetectionService()
    
    assert service.is_supported("en") is True


def test_is_supported_french() -> None:
    """Test is_supported returns True for French."""
    service = LanguageDetectionService()
    
    assert service.is_supported("fr") is True


def test_is_supported_unsupported() -> None:
    """Test is_supported returns False for unsupported language."""
    service = LanguageDetectionService()
    
    assert service.is_supported("es") is False
