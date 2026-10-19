
from database import Database


class LMSModels:
    """Database operations for the Learning Management System."""

    def __init__(self):
        self.database = Database()

    # ==================== COURSES ====================

    def create_course(self, title, description, instructor_id):
        if not title.strip():
            return False, "Course title is required."

        result = self.database.insert(
            """
            INSERT INTO courses (title, description, instructor_id)
            VALUES (%s, %s, %s)
            """,
            (title.strip(), description.strip(), instructor_id)
        )

        if result is None:
            return False, "Unable to create course."

        return True, "Course created successfully."

    def get_courses(self):
        return self.database.fetch_all(
            """
            SELECT id, title, description, instructor_id
            FROM courses
            ORDER BY id DESC
            """
        )

    def get_course(self, course_id):
        return self.database.fetch_one(
            """
            SELECT id, title, description, instructor_id
            FROM courses
            WHERE id = %s
            LIMIT 1
            """,
            (course_id,)
        )

    # ==================== ENROLLMENTS ====================

    def enroll_student(self, student_id, course_id):
        existing = self.database.fetch_one(
            """
            SELECT id
            FROM enrollments
            WHERE student_id = %s AND course_id = %s
            LIMIT 1
            """,
            (student_id, course_id)
        )

        if existing is not None:
            return False, "Student is already enrolled in this course."

        result = self.database.insert(
            """
            INSERT INTO enrollments (student_id, course_id)
            VALUES (%s, %s)
            """,
            (student_id, course_id)
        )

        if result is None:
            return False, "Unable to enroll student."

        return True, "Student enrolled successfully."

    def get_student_courses(self, student_id):
        return self.database.fetch_all(
            """
            SELECT c.id, c.title, c.description
            FROM courses c
            INNER JOIN enrollments e ON e.course_id = c.id
            WHERE e.student_id = %s
            ORDER BY c.id DESC
            """,
            (student_id,)
        )

    # ==================== LESSONS ====================

    def create_lesson(self, course_id, title, content):
        if not title.strip():
            return False, "Lesson title is required."

        result = self.database.insert(
            """
            INSERT INTO lessons (course_id, title, content)
            VALUES (%s, %s, %s)
            """,
            (course_id, title.strip(), content.strip())
        )

        if result is None:
            return False, "Unable to create lesson."

        return True, "Lesson created successfully."

    def get_course_lessons(self, course_id):
        return self.database.fetch_all(
            """
            SELECT id, course_id, title, content
            FROM lessons
            WHERE course_id = %s
            ORDER BY id
            """,
            (course_id,)
        )

    # ==================== ASSIGNMENTS ====================

    def create_assignment(self, course_id, title, description):
        if not title.strip():
            return False, "Assignment title is required."

        result = self.database.insert(
            """
            INSERT INTO assignments (course_id, title, description)
            VALUES (%s, %s, %s)
            """,
            (course_id, title.strip(), description.strip())
        )

        if result is None:
            return False, "Unable to create assignment."

        return True, "Assignment created successfully."

    def get_course_assignments(self, course_id):
        return self.database.fetch_all(
            """
            SELECT id, course_id, title, description
            FROM assignments
            WHERE course_id = %s
            ORDER BY id DESC
            """,
            (course_id,)
        )

    # ==================== SUBMISSIONS ====================

    def submit_assignment(self, assignment_id, student_id, answer):
        if not answer.strip():
            return False, "Your submission cannot be empty."

        result = self.database.insert(
            """
            INSERT INTO submissions
                (assignment_id, student_id, answer)
            VALUES (%s, %s, %s)
            """,
            (assignment_id, student_id, answer.strip())
        )

        if result is None:
            return False, "Unable to submit assignment."

        return True, "Assignment submitted successfully."

    # ==================== QUIZZES ====================

    def create_quiz(self, course_id, title):
        if not title.strip():
            return False, "Quiz title is required."

        result = self.database.insert(
            """
            INSERT INTO quizzes (course_id, title)
            VALUES (%s, %s)
            """,
            (course_id, title.strip())
        )

        if result is None:
            return False, "Unable to create quiz."

        return True, "Quiz created successfully."

    def get_course_quizzes(self, course_id):
        return self.database.fetch_all(
            """
            SELECT id, course_id, title
            FROM quizzes
            WHERE course_id = %s
            ORDER BY id DESC
            """,
            (course_id,)
        )

    # ==================== QUESTIONS ====================

    def create_question(
        self,
        quiz_id,
        question_text,
        option_a,
        option_b,
        option_c,
        option_d,
        correct_answer
    ):
        correct_answer = correct_answer.strip().upper()

        if correct_answer not in ("A", "B", "C", "D"):
            return False, "Correct answer must be A, B, C, or D."

        if not question_text.strip():
            return False, "Question text is required."

        result = self.database.insert(
            """
            INSERT INTO questions
                (quiz_id, question_text, option_a, option_b,
                 option_c, option_d, correct_answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                quiz_id,
                question_text.strip(),
                option_a.strip(),
                option_b.strip(),
                option_c.strip(),
                option_d.strip(),
                correct_answer
            )
        )

        if result is None:
            return False, "Unable to create question."

        return True, "Question created successfully."

    def get_quiz_questions(self, quiz_id):
        return self.database.fetch_all(
            """
            SELECT id, quiz_id, question_text,
                   option_a, option_b, option_c, option_d
            FROM questions
            WHERE quiz_id = %s
            ORDER BY id
            """,
            (quiz_id,)
        )

    # ==================== QUIZ RESULTS ====================

    def save_quiz_result(self, quiz_id, student_id, score):
        result = self.database.insert(
            """
            INSERT INTO quiz_results (quiz_id, student_id, score)
            VALUES (%s, %s, %s)
            """,
            (quiz_id, student_id, score)
        )

        if result is None:
            return False, "Unable to save quiz result."

        return True, "Quiz result saved successfully."

    def get_student_results(self, student_id):
        return self.database.fetch_all(
            """
            SELECT qr.id, qr.quiz_id, q.title, qr.score
            FROM quiz_results qr
            INNER JOIN quizzes q ON q.id = qr.quiz_id
            WHERE qr.student_id = %s
            ORDER BY qr.id DESC
            """,
            (student_id,)
        )
