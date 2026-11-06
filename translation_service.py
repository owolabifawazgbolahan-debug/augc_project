
import argostranslate.package
import argostranslate.translate


class TranslationService:
    """Translate LMS questions from English."""

    LANGUAGES = {
        "english": "en",
        "yoruba": "yo",
        "hausa": "ha",
        "igbo": "ig",
        "french": "fr",
        "spanish": "es",
        "arabic": "ar",
        "german": "de",
        "portuguese": "pt",
        "chinese": "zh",
        "hindi": "hi"
    }

    def translate(self, text, target_language):
        if not text:
            return text

        language = target_language.strip().lower()
        target_code = self.LANGUAGES.get(language)

        if target_code is None:
            return f"Unsupported language: {language}"

        if target_code == "en":
            return text

        try:
            installed = argostranslate.translate.get_installed_languages()

            source = next(
                (lang for lang in installed if lang.code == "en"),
                None
            )

            target = next(
                (lang for lang in installed
                 if lang.code == target_code),
                None
            )

            if source and target:
                translation = source.get_translation(target)
                return translation.translate(str(text))

            print(f"Looking for an English-to-{language} model...")

            argostranslate.package.update_package_index()
            packages = argostranslate.package.get_available_packages()

            package = next(
                (p for p in packages
                 if p.from_code == "en"
                 and p.to_code == target_code),
                None
            )

            if package is None:
                return (
                    f"Translation model unavailable for {language}. "
                    "Please choose another language."
                )

            downloaded = package.download()
            argostranslate.package.install_from_path(downloaded)

            installed = argostranslate.translate.get_installed_languages()

            source = next(
                (lang for lang in installed if lang.code == "en"),
                None
            )

            target = next(
                (lang for lang in installed
                 if lang.code == target_code),
                None
            )

            if not source or not target:
                return "The translation model could not be loaded."

            translation = source.get_translation(target)
            return translation.translate(str(text))

        except Exception as error:
            print("Translation error:", error)
            return "Translation failed. Check your internet connection and try again."
