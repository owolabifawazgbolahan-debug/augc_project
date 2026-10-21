
# from deep_translator import GoogleTranslator


# class TranslationService:


#     SUPPORTED_LANGUAGES = {
#         "english": "en",
#         "yoruba": "yo",
#         "hausa": "ha",
#         "igbo": "ig",
#         "french": "fr",
#         "spanish": "es",
#         "arabic": "ar",
#         "german": "de",
#         "portuguese": "pt",
#         "chinese": "zh-CN",
#         "hindi": "hi"
#     }

#     def get_supported_languages(self):
#         return list(self.SUPPORTED_LANGUAGES.keys())

#     def translate_text(self, text, target_language, source_language="english"):
#         """Translate a single piece of text."""

#         if not isinstance(text, str) or not text.strip():
#             return False, "Text cannot be empty."

#         if not isinstance(target_language, str):
#             return False, "Invalid target language."

#         if not isinstance(source_language, str):
#             return False, "Invalid source language."

#         source_language = source_language.strip().lower()
#         target_language = target_language.strip().lower()

#         if source_language not in self.SUPPORTED_LANGUAGES:
#             return False, "Unsupported source language."

#         if target_language not in self.SUPPORTED_LANGUAGES:
#             return False, "Unsupported target language."

#         if source_language == target_language:
#             return True, text

#         try:
#             translator = GoogleTranslator(
#                 source=self.SUPPORTED_LANGUAGES[source_language],
#                 target=self.SUPPORTED_LANGUAGES[target_language]
#             )

#             translated_text = translator.translate(text.strip())

#             if not translated_text:
#                 return False, "Translation returned no result."

#             return True, translated_text

#         except Exception as error:
#             print("Translation service error:", error)
#             return False, (
#                 "Translation is temporarily unavailable. "
#                 "Check your internet connection and try again."
#             )

#     def translate_quiz_question(
#         self,
#         question,
#         option_a,
#         option_b,
#         option_c,
#         option_d,
#         target_language,
#         source_language="english"
#     ):
#         """Translate a question and its four answer options."""

#         original_texts = [
#             question, option_a, option_b, option_c, option_d
#         ]

#         translated_texts = []

#         for text in original_texts:
#             success, result = self.translate_text(
#                 text,
#                 target_language,
#                 source_language
#             )

#             if not success:
#                 return False, result

#             translated_texts.append(result)

#         return True, {
#             "question": translated_texts[0],
#             "option_a": translated_texts[1],
#             "option_b": translated_texts[2],
#             "option_c": translated_texts[3],
#             "option_d": translated_texts[4]
#         }
