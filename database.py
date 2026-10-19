
import mysql.connector as sql


class Database:
    """Handles MySQL operations for the LMS."""

    HOST = "127.0.0.1"
    PORT = 3306
    USER = "root"
    PASSWORD = ""
    DATABASE = "augc_project"

    def connect(self):
        """Create a new MySQL connection."""

        try:
            connection = sql.connect(
                host=self.HOST,
                port=self.PORT,
                user=self.USER,
                password=self.PASSWORD,
                database=self.DATABASE
            )

            return connection

        except sql.Error as error:
            print(f"Database connection error: {error}")
            return None

    def fetch_one(self, query, values=()):
        """Fetch one record using a parameterized query."""

        connection = self.connect()

        if connection is None:
            return None

        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, values)
            return cursor.fetchone()

        except sql.Error as error:
            print(f"Query error: {error}")
            return None

        finally:
            cursor.close()
            connection.close()

    def fetch_all(self, query, values=()):
        """Fetch multiple records using a parameterized query."""

        connection = self.connect()

        if connection is None:
            return []

        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, values)
            return cursor.fetchall()

        except sql.Error as error:
            print(f"Query error: {error}")
            return []

        finally:
            cursor.close()
            connection.close()

    def execute(self, query, values=()):
        """Execute INSERT, UPDATE or DELETE statements."""

        connection = self.connect()

        if connection is None:
            return False

        cursor = connection.cursor()

        try:
            cursor.execute(query, values)
            connection.commit()
            return True

        except sql.Error as error:
            connection.rollback()
            print(f"Database operation failed: {error}")
            return False

        finally:
            cursor.close()
            connection.close()

    def insert(self, query, values=()):
        """Insert a record and return its new ID."""

        connection = self.connect()

        if connection is None:
            return None

        cursor = connection.cursor()

        try:
            cursor.execute(query, values)
            connection.commit()
            return cursor.lastrowid

        except sql.Error as error:
            connection.rollback()
            print(f"Insert failed: {error}")
            return None

        finally:
            cursor.close()
            connection.close()

    def table_exists(self, table_name):
        """Check whether a table exists in the selected database."""

        allowed_tables = {
            "users",
            "courses",
            "enrollments",
            "lessons",
            "assignments",
            "submissions",
            "quizzes",
            "questions",
            "quiz_results"
        }

        if table_name not in allowed_tables:
            return False

        result = self.fetch_one(
            """
            SELECT TABLE_NAME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = %s
            """,
            (self.DATABASE, table_name)
        )

        return result is not None
