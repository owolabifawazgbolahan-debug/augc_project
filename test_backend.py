
from lms_config import lms_config

system = lms_config()

print("\nLMS BACKEND TEST")

if system.connect():
    print("MySQL connection: SUCCESS")
    system.close()
else:
    print("MySQL connection: FAILED")
    print("Check that MySQL is running and augc_project exists.")

print("\nEmail validation:", system.validate_email("student@example.com"))
print("Password validation:", system.validate_password("Test@1234"))

print("\nBackend test completed.")
