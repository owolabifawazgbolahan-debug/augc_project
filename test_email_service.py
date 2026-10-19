
from email_service import EmailService

service = EmailService()

recipient = input("Enter the email address to receive the test: ").strip()
code = service.generate_code()

print("Generated verification code:", code)

success, message = service.send_verification_code(
    recipient,
    code
)

print(message)
# bhfbyzlkeixbyqug
