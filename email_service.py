
import random
import string
import smtplib
import ssl
import time
from email.mime.text import MIMEText


class EmailService:
    """Sends and verifies email verification codes using Gmail SMTP."""

    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 465

    def __init__(self, sender_email=None, app_password=None):
        self.sender_email = sender_email or "owolabigbolahanfawaz@gmail.com"
        self.app_password = app_password or "bhfbyzlkeixbyqug"
        self.verification_codes = {}

    def configure(self):
        """Request Gmail credentials if they are not provided."""

        if not self.sender_email:
            self.sender_email = input(
                "Enter your Gmail address: "
            ).strip()

        if not self.app_password:
            self.app_password = input(
                "Enter your Gmail App Password: "
            ).strip().replace(" ", "")

        return bool(self.sender_email and self.app_password)

    def generate_code(self):
        """Generate a six-digit verification code."""

        return "".join(
            random.choices(string.digits, k=6)
        )

    def send_verification_code(self, recipient_email, code):
        """Send a plain-text verification email."""

        if not self.configure():
            return False, "Email configuration is incomplete."

        recipient_email = recipient_email.strip().lower()

        message = MIMEText(
            "Welcome to the SQI Learning Management System.\n\n"
            f"Your email verification code is: {code}\n\n"
            "This code expires in 5 minutes.\n"
            "You have a maximum of 5 incorrect attempts.\n\n"
            "If you did not create this account, ignore this email.",
            "plain"
        )

        message["Subject"] = "SQI LMS Email Verification"
        message["From"] = self.sender_email
        message["To"] = recipient_email

        try:
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(
                self.SMTP_HOST,
                self.SMTP_PORT,
                context=context,
                timeout=20
            ) as server:
                server.login(
                    self.sender_email,
                    self.app_password
                )

                server.sendmail(
                    self.sender_email,
                    recipient_email,
                    message.as_string()
                )

            self.verification_codes[recipient_email] = {
                "code": code,
                "expires_at": time.monotonic() + 300,
                "attempts": 0
            }

            return True, "Verification email sent successfully."

        except (smtplib.SMTPException, OSError) as error:
            print(f"Email sending failed: {error}")
            return False, "Unable to send the verification email."

    def verify_code(self, recipient_email, entered_code):
        """Verify the code, expiry time, and attempt limit."""

        if not isinstance(recipient_email, str):
            return False, "Invalid email address."

        if not isinstance(entered_code, str):
            return False, "Incorrect verification code."

        email = recipient_email.strip().lower()
        record = self.verification_codes.get(email)

        if record is None:
            return False, "No verification code found. Request a new one."

        if time.monotonic() >= record["expires_at"]:
            del self.verification_codes[email]
            return False, "Verification code expired. Request a new one."

        if record["attempts"] >= 5:
            del self.verification_codes[email]
            return False, "Too many attempts. Request a new code."

        if record["code"] != entered_code.strip():
            record["attempts"] += 1

            if record["attempts"] >= 5:
                del self.verification_codes[email]
                return False, "Too many attempts. Request a new code."

            remaining = 5 - record["attempts"]

            return False, (
                f"Incorrect verification code. "
                f"{remaining} attempts remaining."
            )

        del self.verification_codes[email]

        return True, "Email verification successful."
