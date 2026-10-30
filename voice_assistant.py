
# import pyttsx3


# class VoiceAssistant:
#     def __init__(self):
#         self.engine = pyttsx3.init()

#     def speak(self, message):
#         print("Assistant:", message)
#         self.engine.say(message)
#         self.engine.runAndWait()

#     def start(self):
#         self.speak("Welcome to the Learning Management System.")

#         while True:
#             print("\n1. Ask a question")
#             print("2. Exit")

#             choice = input("Choose an option: ")

#             if choice == "1":
#                 question = input("Enter your question: ")
#                 self.speak("You asked: " + question)

#             elif choice == "2":
#                 self.speak("Goodbye.")
#                 break

#             else:
#                 self.speak("Invalid choice.")


# if __name__ == "__main__":
#     assistant = VoiceAssistant()
#     assistant.start()
