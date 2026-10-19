
from deep_translator import GoogleTranslator


class TranslationService:
    """Translates LMS text between supported languages."""

    SUPPORTED_LANGUAGES = {
        "english": "en",
        "yoruba": "yo",
        "hausa": "ha",
        "igbo": "ig",
        "french": "fr",
        "spanish": "es",
        "arabic": "ar",
        "german": "de",
        "portuguese": "pt",
        "chinese": "zh-CN",
        "hindi": "hi"
    }

    def get_supported_languages(self):
        """Return the available languages."""

        return list(self.SUPPORTED_LANGUAGES.keys())

    def translate_text(self, text, target_language, source_language="english"):
        """Translate text into the selected language."""

        if not isinstance(text, str) or not text.strip():
            return False, "Text cannot be empty."

        source_language = source_language.strip().lower()
        target_language = target_language.strip().lower()

        if source_language not in self.SUPPORTED_LANGUAGES:
            return False, "Unsupported source language."

        if target_language not in self.SUPPORTED_LANGUAGES:
            return False, "Unsupported target language."

        if source_language == target_language:
            return True, text

        try:
            translator = GoogleTranslator(
                source=self.SUPPORTED_LANGUAGES[source_language],
                target=self.SUPPORTED_LANGUAGES[target_language]
            )

            translated_text = translator.translate(text)

            if not translated_text:
                return False, "Translation returned no result."

            return True, translated_text

        except Exception as error:
            print(f"Translation error: {error}")
            return False, "Translation failed. Check your internet connection."
