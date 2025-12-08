"""Language detection service using langdetect."""
from langdetect import LangDetectException, detect

from eva_rag.config import settings


class LanguageDetectionService:
    """Detect document language for bilingual EN-CA/FR-CA support."""
    
    def __init__(self) -> None:
        """Initialize language detection service."""
        self.supported_languages = settings.supported_languages
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text content.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Two-letter language code ('en' or 'fr')
            Defaults to 'en' if detection fails or language unsupported
            
        Examples:
            >>> service = LanguageDetectionService()
            >>> service.detect_language("Hello world")
            'en'
            >>> service.detect_language("Bonjour le monde")
            'fr'
        """
        if not text or len(text.strip()) < 10:
            # Too short for reliable detection, default to English
            return "en"
        
        try:
            # Use first 1000 characters for detection (sufficient and faster)
            sample = text[:1000]
            detected = detect(sample)
            
            # Map detected language to supported languages
            if detected in self.supported_languages:
                return detected
            
            # Default to English for unsupported languages
            return "en"
            
        except LangDetectException:
            # Detection failed, default to English
            return "en"
    
    def is_supported(self, language: str) -> bool:
        """
        Check if language is supported.
        
        Args:
            language: Two-letter language code
            
        Returns:
            True if language is supported
        """
        return language in self.supported_languages
