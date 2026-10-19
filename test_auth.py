
from auth import Auth

auth = Auth()

print("========== AUTHENTICATION TEST ==========")

print(
    "Valid email:",
    auth.validate_email("student@example.com")
)

print(
    "Invalid email:",
    auth.validate_email("student@")
)

print(
    "Strong password:",
    auth.validate_password("Test@1234")
)

print(
    "Weak password:",
    auth.validate_password("password")
)

hashed = auth.hash_password("Test@1234")

print(
    "Password hash verification:",
    auth.check_password("Test@1234", hashed)
)

print("=========================================")
