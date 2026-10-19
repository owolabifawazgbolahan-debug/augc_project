
import re
import mysql.connector as sql
import bcrypt


class lms_config:
    """Main backend for the SQI Learning Management System."""

    APP_NAME = "SQI Learning Management System"

    HOST = "127.0.0.1"
    PORT = 3306
    USER = "root"
    PASSWORD = ""
    DATABASE = "augc_project"

    ALLOWED_ROLES = ("student", "instructor", "admin")

    def __init__(self):
        self.connection = None
        self.cursor = None


    def connect(self):
        """Connect to the MySQL database."""

        try:
            self.connection = sql.connect(
                host=self.HOST,
                port=self.PORT,
                user=self.USER,
                password=self.PASSWORD,
                database=self.DATABASE
            )

            self.cursor = self.connection.cursor(dictionary=True)
            return True

        except sql.Error as error:
            print(f"MySQL connection failed: {error}")
            self.connection = None
            self.cursor = None
            return False

    def close(self):
        """Close the cursor and database connection."""

        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None

        if self.connection is not None and self.connection.is_connected():
            self.connection.close()

        self.connection = None

    def validate_email(self, email):
        """Check whether an email address is valid."""

        if not isinstance(email, str):
            return False

        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        return re.fullmatch(pattern, email.strip()) is not None

    def validate_password(self, password):
        """
        Require at least:
        - 8 characters
        - One uppercase letter
        - One lowercase letter
        - One number
        - One special character
        """

        if not isinstance(password, str) or len(password) < 8:
            return False

        if not re.search(r"[A-Z]", password):
            return False

        if not re.search(r"[a-z]", password):
            return False

        if not re.search(r"[0-9]", password):
            return False

        if not re.search(r"[^A-Za-z0-9]", password):
            return False

        return True


    def hash_password(self, password):
        """Hash a password using bcrypt."""

        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        return hashed.decode("utf-8")

    def verify_password(self, password, password_hash):
        """Compare a password against its stored hash."""

        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8")
            )
        except (ValueError, TypeError, AttributeError):
            return False


    def email_exists(self, email):
        """Check whether an email is already registered."""

        if not self.connect():
            return None

        try:
            self.cursor.execute(
                "SELECT id FROM users WHERE email = %s LIMIT 1",
                (email.strip().lower(),)
            )

            return self.cursor.fetchone() is not None

        except sql.Error as error:
            print(f"Email lookup failed: {error}")
            return None

        finally:
            self.close()

    def register_user(self, first_name, last_name, email, password):
        """Register a new student account."""

        first_name = first_name.strip()
        last_name = last_name.strip()
        email = email.strip().lower()

        if not first_name or not last_name:
            return False, "First name and last name are required."

        if not self.validate_email(email):
            return False, "Please enter a valid email address."

        if not self.validate_password(password):
            return False, (
                "Password must contain at least 8 characters, "
                "an uppercase letter, a lowercase letter, "
                "a number and a special character."
            )

        if not self.connect():
            return False, "Unable to connect to the database."

        try:
            self.cursor.execute(
                "SELECT id FROM users WHERE email = %s LIMIT 1",
                (email,)
            )

            if self.cursor.fetchone():
                return False, "This email is already registered."

            password_hash = self.hash_password(password)

            self.cursor.execute(
                """
                INSERT INTO users
                    (first_name, last_name, email, password_hash, role,
                     email_verified, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    first_name,
                    last_name,
                    email,
                    password_hash,
                    "student",
                    False,
                    True
                )
            )

            self.connection.commit()

            return True, (
                "Account created successfully. "
                "Email verification is still required."
            )

        except sql.Error as error:
            if self.connection and self.connection.is_connected():
                self.connection.rollback()

            print(f"Registration failed: {error}")
            return False, "Registration failed. Please try again."

        finally:
            self.close()

    def login_user(self, email, password):
        """Authenticate a user and return their account details."""

        email = email.strip().lower()

        if not self.validate_email(email):
            return False, "Invalid email address."

        if not self.connect():
            return False, "Unable to connect to the database."

        try:
            self.cursor.execute(
                """
                SELECT id, first_name, last_name, email,
                       password_hash, role, email_verified, is_active
                FROM users
                WHERE email = %s
                LIMIT 1
                """,
                (email,)
            )

            user = self.cursor.fetchone()

            if user is None:
                return False, "Incorrect email or password."

            if not self.verify_password(
                password,
                user["password_hash"]
            ):
                return False, "Incorrect email or password."

            if not user["is_active"]:
                return False, "This account has been deactivated."

            if not user["email_verified"]:
                return False, "Please verify your email before logging in."

            user.pop("password_hash", None)

            return True, user

        except sql.Error as error:
            print(f"Login failed: {error}")
            return False, "Login failed. Please try again."

        finally:
            self.close()


    def has_role(self, user, allowed_roles):
        """Check whether the logged-in user has permission."""

        if not isinstance(user, dict):
            return False

        if isinstance(allowed_roles, str):
            allowed_roles = (allowed_roles,)

        return user.get("role") in allowed_roles

    def require_role(self, user, allowed_roles):
        """Raise an error when a user lacks permission."""

        if not self.has_role(user, allowed_roles):
            raise PermissionError(
                "You do not have permission to perform this action."
            )

        return True

    def get_user(self, user_id):
        """Retrieve a user's public account details."""

        if not self.connect():
            return None

        try:
            self.cursor.execute(
                """
                SELECT id, first_name, last_name, email,
                       role, email_verified, is_active
                FROM users
                WHERE id = %s
                LIMIT 1
                """,
                (user_id,)
            )

            return self.cursor.fetchone()

        except sql.Error as error:
            print(f"User lookup failed: {error}")
            return None

        finally:
            self.close()
