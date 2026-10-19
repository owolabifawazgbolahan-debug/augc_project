
import re
import bcrypt
from database import Database


class Auth:
    """Handles registration, login, and user roles."""

    def __init__(self):
        self.database = Database()

    def validate_email(self, email):
        pattern = (
            r"^[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        )
        return bool(re.fullmatch(pattern, email.strip()))

    def validate_password(self, password):
        if len(password) < 8:
            return False, "Password must contain at least 8 characters."

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain an uppercase letter."

        if not re.search(r"[a-z]", password):
            return False, "Password must contain a lowercase letter."

        if not re.search(r"[0-9]", password):
            return False, "Password must contain a number."

        if not re.search(r"[^A-Za-z0-9]", password):
            return False, "Password must contain a special character."

        return True, "Password is valid."

    def hash_password(self, password):
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password, password_hash):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8")
            )
        except (ValueError, TypeError):
            return False

    def register(
        self, first_name, last_name, email, password,
        role="student"
    ):
        first_name = first_name.strip()
        last_name = last_name.strip()
        email = email.strip().lower()
        role = role.strip().lower()

        if not first_name or not last_name:
            return False, "First name and last name are required."

        if not self.validate_email(email):
            return False, "Please enter a valid email address."

        if role not in ("student", "instructor"):
            return False, "Choose student or instructor."

        password_valid, message = self.validate_password(password)

        if not password_valid:
            return False, message

        existing_user = self.database.fetch_one(
            "SELECT id FROM users WHERE email = %s LIMIT 1",
            (email,)
        )

        if existing_user:
            return False, "An account with this email already exists."

        password_hash = self.hash_password(password)

        result = self.database.insert(
            """
            INSERT INTO users
                (first_name, last_name, email, password_hash,
                 role, email_verified, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                first_name, last_name, email, password_hash,
                role, False, True
            )
        )

        if result is None:
            return False, "Unable to create your account."

        return True, (
            f"Account created successfully as {role}. "
            "Please verify your email."
        )

    def create_admin(
        self, first_name, last_name, email, password
    ):
        """Create an administrator through a controlled setup script."""

        first_name = first_name.strip()
        last_name = last_name.strip()
        email = email.strip().lower()

        if not first_name or not last_name:
            return False, "First name and last name are required."

        if not self.validate_email(email):
            return False, "Please enter a valid email address."

        password_valid, message = self.validate_password(password)

        if not password_valid:
            return False, message

        existing_user = self.database.fetch_one(
            "SELECT id FROM users WHERE email = %s LIMIT 1",
            (email,)
        )

        if existing_user:
            return False, "An account with this email already exists."

        existing_admin = self.database.fetch_one(
            "SELECT id FROM users WHERE role = %s LIMIT 1",
            ("admin",)
        )

        if existing_admin:
            return False, (
                "An administrator already exists. "
                "A new admin cannot be created using this setup."
            )

        password_hash = self.hash_password(password)

        result = self.database.insert(
            """
            INSERT INTO users
                (first_name, last_name, email, password_hash,
                 role, email_verified, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                first_name, last_name, email, password_hash,
                "admin", True, True
            )
        )

        if result is None:
            return False, "Unable to create the administrator account."

        return True, "Administrator account created successfully."

    def login(self, email, password):
        email = email.strip().lower()

        user = self.database.fetch_one(
            """
            SELECT id, first_name, last_name, email,
                   password_hash, role, email_verified, is_active
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        if not user:
            return False, "Incorrect email or password."

        if not self.check_password(password, user["password_hash"]):
            return False, "Incorrect email or password."

        if not user["is_active"]:
            return False, "Your account has been deactivated."

        if not user["email_verified"]:
            return False, "Please verify your email before logging in."

        return True, user

    def is_email_verified(self, user_id):
        user = self.database.fetch_one(
            "SELECT email_verified FROM users WHERE id = %s",
            (user_id,)
        )
        return bool(user and user["email_verified"])

    def mark_email_verified(self, email):
        email = email.strip().lower()

        user = self.database.fetch_one(
            "SELECT id FROM users WHERE email = %s LIMIT 1",
            (email,)
        )

        if not user:
            return False, "Account not found."

        result = self.database.execute(
            "UPDATE users SET email_verified = %s WHERE id = %s",
            (True, user["id"])
        )

        if result is False:
            return False, "Unable to verify your email."

        return True, "Email verified successfully."

    def has_role(self, user, allowed_roles):
        return user.get("role") in allowed_roles
