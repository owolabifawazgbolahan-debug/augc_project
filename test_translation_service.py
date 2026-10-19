
from translation_service import TranslationService

translator = TranslationService()

print("Supported languages:")
print(", ".join(translator.get_supported_languages()))

text = input("\nEnter text to translate: ")
target = input("Translate into which language? ").strip()

success, result = translator.translate_text(
    text,
    target
)

if success:
    print("\nTranslated text:")
    print(result)
else:
    print("\nError:")
    print(result)
