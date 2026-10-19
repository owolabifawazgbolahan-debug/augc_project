
from database import Database

database = Database()

print("DATABASE MODULE TEST")

tables = [
    "users",
    "courses",
    "enrollments",
    "lessons",
    "assignments",
    "submissions",
    "quizzes",
    "questions",
    "quiz_results"
]

for table in tables:
    if database.table_exists(table):
        print(f"[OK] {table}")
    else:
        print(f"[MISSING] {table}")

print(".......................")
