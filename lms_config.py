import re
import mysql.connector as sql
import bcrypt


class lms_config:
    """Backend for the SQI Learning Management System."""

    APP_NAME = "SQI Learning Management System"

    # Database settings
    HOST = "127.0.0.1"
    PORT = 3306
    USER = "root"
    PASSWORD = ""
    DATABASE = "augc_project"

    # Roles allowed in the LMS
    ALLOWED_ROLES = ("student", "instructor", "admin")

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

    def __init__(self):
        self.connection = None
        self.cursor = None

    # ---------------- DATABASE ----------------

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
            print(f"Database connection failed: {error}")
            self.connection = None
            self.cursor = None
            return False

    def close(self):
        """Close the database connection."""

        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None

        if self.connection is not None:
            if self.connection.is_connected():
                self.connection.close()

        self.connection = None

    # ---------------- EMAIL VALIDATION ----------------

    def validate_email(self, email):
        """Check whether an email address is valid."""

        if not isinstance(email, str):
            return False

        pattern = (
            r"^[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        )

        return re.fullmatch(pattern, email.strip()) is not None

    # ---------------- PASSWORD SECURITY ----------------

    def validate_password(self, password):
        """
        A password must contain:
        - At least 8 characters
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
        """Turn a password into a secure hash before saving it."""

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        return hashed_password.decode("utf-8")

    def verify_password(self, password, password_hash):
        """Check whether a password matches its saved hash."""

        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8")
            )

        except (ValueError, TypeError, AttributeError):
            return False

    # ---------------- CHECK EMAIL ----------------

    def email_exists(self, email):
        """Check whether an email is already registered."""

        if not isinstance(email, str):
            return False

        if not self.connect():
            return None

        try:
            self.cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                LIMIT 1
                """,
                (email.strip().lower(),)
            )

            return self.cursor.fetchone() is not None

        except sql.Error as error:
            print(f"Email lookup failed: {error}")
            return None

        finally:
            self.close()

    # ---------------- REGISTER USER ----------------

    def register_user(self, first_name, last_name, email, password):
        """Create a new student account."""

        if not all(
            isinstance(value, str)
            for value in (first_name, last_name, email, password)
        ):
            return False, "Please enter valid account details."

        first_name = first_name.strip()
        last_name = last_name.strip()
        email = email.strip().lower()

        if not first_name or not last_name:
            return False, "First name and last name are required."

        if not self.validate_email(email):
            return False, "Please enter a valid email address."

        if not self.validate_password(password):
            return False, (
                "Your password must contain at least 8 characters, "
                "an uppercase letter, a lowercase letter, "
                "a number and a special character."
            )

        if not self.connect():
            return False, "Unable to connect to the database."

        try:
            self.cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                LIMIT 1
                """,
                (email,)
            )

            if self.cursor.fetchone():
                return False, "This email is already registered."

            password_hash = self.hash_password(password)

            self.cursor.execute(
                """
                INSERT INTO users (
                    first_name,
                    last_name,
                    email,
                    password_hash,
                    role,
                    email_verified,
                    is_active,
                    preferred_language
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    first_name,
                    last_name,
                    email,
                    password_hash,
                    "student",
                    False,
                    True,
                    "english"
                )
            )

            self.connection.commit()

            return True, (
                "Account created successfully. "
                "Please verify your email before logging in."
            )

        except sql.Error as error:
            if self.connection and self.connection.is_connected():
                self.connection.rollback()

            print(f"Registration failed: {error}")
            return False, "Registration failed. Please try again."

        finally:
            self.close()

    # ---------------- LOGIN USER ----------------

    def login_user(self, email, password):
        """Check login details and return the user's information."""

        if not isinstance(email, str) or not isinstance(password, str):
            return False, "Please enter a valid email and password."

        email = email.strip().lower()

        if not self.validate_email(email):
            return False, "Invalid email address."

        if not self.connect():
            return False, "Unable to connect to the database."

        try:
            self.cursor.execute(
                """
                SELECT
                    id,
                    first_name,
                    last_name,
                    email,
                    password_hash,
                    role,
                    email_verified,
                    is_active,
                    preferred_language
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
                return False, (
                    "Please verify your email before logging in."
                )

            # Never return the password hash to the application.
            user.pop("password_hash", None)

            return True, user

        except sql.Error as error:
            print(f"Login failed: {error}")
            return False, "Login failed. Please try again."

        finally:
            self.close()

    # ---------------- LANGUAGE SETTINGS ----------------

    def set_preferred_language(self, user_id, language):
        """Save the language selected by a user."""

        if not isinstance(language, str):
            return False, "Please select a valid language."

        language = language.strip().lower()

        if language not in self.SUPPORTED_LANGUAGES:
            return False, "This language is not supported."

        if not self.connect():
            return False, "Unable to connect to the database."

        try:
            self.cursor.execute(
                """
                UPDATE users
                SET preferred_language = %s
                WHERE id = %s
                """,
                (language, user_id)
            )

            # Save the change to the database.
            self.connection.commit()

            if self.cursor.rowcount == 0:
                # A zero row count can mean the language was
                # already selected, so check whether the user exists.
                self.cursor.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (user_id,)
                )

                if self.cursor.fetchone() is None:
                    return False, "User not found."

            return True, "Your language preference has been saved."

        except sql.Error as error:
            if self.connection and self.connection.is_connected():
                self.connection.rollback()

            print(f"Language update failed: {error}")
            return False, "Could not save your language preference."

        finally:
            self.close()

    def get_preferred_language(self, user_id):
        """Find the language saved for a particular user."""

        if not self.connect():
            return "english"

        try:
            self.cursor.execute(
                """
                SELECT preferred_language
                FROM users
                WHERE id = %s
                LIMIT 1
                """,
                (user_id,)
            )

            user = self.cursor.fetchone()

            if user and user.get("preferred_language"):
                language = user["preferred_language"].lower()

                if language in self.SUPPORTED_LANGUAGES:
                    return language

            return "english"

        except sql.Error as error:
            print(f"Language lookup failed: {error}")
            return "english"

        finally:
            self.close()

    # ---------------- USER ROLES ----------------

    def has_role(self, user, allowed_roles):
        """Check whether a user has permission to perform an action."""

        if not isinstance(user, dict):
            return False

        if isinstance(allowed_roles, str):
            allowed_roles = (allowed_roles,)

        return user.get("role") in allowed_roles

    def require_role(self, user, allowed_roles):
        """Stop a user from performing an action without permission."""

        if not self.has_role(user, allowed_roles):
            raise PermissionError(
                "You do not have permission to perform this action."
            )

        return True

    # ---------------- GET USER DETAILS ----------------

    def get_user(self, user_id):
        """Get a user's public account information."""

        if not self.connect():
            return None

        try:
            self.cursor.execute(
                """
                SELECT
                    id,
                    first_name,
                    last_name,
                    email,
                    role,
                    email_verified,
                    is_active,
                    preferred_language
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
