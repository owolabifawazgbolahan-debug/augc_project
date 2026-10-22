
import argostranslate.package
import argostranslate.translate


class TranslationService:
    """Translates LMS content into the student's language."""

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
        "chinese": "zh",
        "hindi": "hi"
    }

    def translate(self, text, target_language):
        if not text:
            return text

        language = target_language.lower().strip()
        target_code = self.SUPPORTED_LANGUAGES.get(language)

        if not target_code:
            return text

        if target_code == "en":
            return text

        try:
            installed_languages = (
                argostranslate.translate.get_installed_languages()
            )

            source = next(
                (lang for lang in installed_languages
                 if lang.code == "en"),
                None
            )

            target = next(
                (lang for lang in installed_languages
                 if lang.code == target_code),
                None
            )

            if not source or not target:
                argostranslate.package.update_package_index()
                packages = argostranslate.package.get_available_packages()

                package = next(
                    (p for p in packages
                     if p.from_code == "en"
                     and p.to_code == target_code),
                    None
                )

                if not package:
                    return (
                        f"[Translation model unavailable for {language}] "
                        f"{text}"
                    )

                argostranslate.package.install_from_path(
                    package.download()
                )

                installed_languages = (
                    argostranslate.translate.get_installed_languages()
                )

                source = next(
                    lang for lang in installed_languages
                    if lang.code == "en"
                )

                target = next(
                    lang for lang in installed_languages
                    if lang.code == target_code
                )

            translation = source.get_translation(target)
            return translation.translate(str(text))

        except Exception as error:
            print("Translation error:", error)
            return text
