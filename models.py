
from database import Database


class LMSModels:
    """Handles database operations for the Learning Management System."""

    def __init__(self):
        self.database = Database()

    def create_course(self, title, description, instructor_id):
        """Create a new course."""

        return self.database.insert(
            """
            INSERT INTO courses (title, description, instructor_id)
            VALUES (%s, %s, %s)
            """,
            (title, description, instructor_id)
        )

    def get_course(self, course_id):
        """Get one course by its ID."""

        return self.database.fetch_one(
            """
            SELECT *
            FROM courses
            WHERE id = %s
            LIMIT 1
            """,
            (course_id,)
        )

    def get_all_courses(self):
        """Get all courses."""

        return self.database.fetch_all(
            """
            SELECT *
            FROM courses
            ORDER BY id DESC
            """
        )
    
    def get_courses(self):
        """Return all available courses."""
        return self.get_all_courses()


    def get_instructor_courses(self, instructor_id):
        """Get courses created by an instructor."""

        return self.database.fetch_all(
            """
            SELECT *
            FROM courses
            WHERE instructor_id = %s
            ORDER BY id DESC
            """,
            (instructor_id,)
        )

    def update_course(self, course_id, title, description):
        """Update a course."""

        return self.database.execute(
            """
            UPDATE courses
            SET title = %s, description = %s
            WHERE id = %s
            """,
            (title, description, course_id)
        )

    def delete_course(self, course_id):
        """Delete a course."""

        return self.database.execute(
            """
            DELETE FROM courses
            WHERE id = %s
            """,
            (course_id,)
        )
    
    def enroll_student(self, student_id, course_id):
        """Enroll a student in a course."""

        student = self.database.fetch_one(
            """
            SELECT id
            FROM users
            WHERE id = %s AND role = 'student'
            LIMIT 1
            """,
            (student_id,)
        )

        if student is None:
            return False, "Student account not found."

        course = self.get_course(course_id)

        if course is None:
            return False, "Course not found."

        existing = self.database.fetch_one(
            """
            SELECT user_id, course_id, status
            FROM enrollments
            WHERE user_id = %s AND course_id = %s
            LIMIT 1
            """,
            (student_id, course_id)
        )

        if existing is not None:
            if existing["status"] == "active":
                return False, "You are already enrolled in this course."

            return False, "An enrollment record already exists for this course."

        result = self.database.insert(
            """
            INSERT INTO enrollments
                (student_id, user_id, course_id, status)
            VALUES (%s, %s, %s, 'active')
            """,
            (student_id, student_id, course_id)
        )

        if result is None:
            return False, "Unable to enroll student."

        return True, "Enrollment successful."


    def get_student_courses(self, student_id):
        """Get courses a student is actively enrolled in."""

        return self.database.fetch_all(
            """
            SELECT courses.*
            FROM courses
            INNER JOIN enrollments
                ON courses.id = enrollments.course_id
            WHERE enrollments.student_id = %s
              AND enrollments.status = 'active'
            ORDER BY courses.id DESC
            """,
            (student_id,)
        )

    def get_course_students(self, course_id):
        """Get students enrolled in a course."""

        return self.database.fetch_all(
            """
            SELECT users.id,
                   users.first_name,
                   users.last_name,
                   users.email
            FROM users
            INNER JOIN enrollments
                ON users.id = enrollments.student_id
            WHERE enrollments.course_id = %s
              AND enrollments.status = 'active'
              AND users.role = 'student'
            ORDER BY users.first_name, users.last_name
            """,
            (course_id,)
        )


    def create_lesson(
        self,
        course_id,
        title,
        content=None,
        video_url=None,
        lesson_order=1
    ):
        """Create a lesson for a course."""

        course = self.get_course(course_id)

        if course is None:
            return False, "Course not found."

        result = self.database.insert(
            """
            INSERT INTO lessons
                (course_id, title, content, video_url, lesson_order)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (course_id, title, content, video_url, lesson_order)
        )

        if result is None:
            return False, "Unable to create lesson."

        return True, "Lesson created successfully."

    def get_lesson(self, lesson_id):
        """Get one lesson."""

        return self.database.fetch_one(
            """
            SELECT *
            FROM lessons
            WHERE id = %s
            LIMIT 1
            """,
            (lesson_id,)
        )

    def get_course_lessons(self, course_id):
        """Get all lessons belonging to a course."""

        return self.database.fetch_all(
            """
            SELECT *
            FROM lessons
            WHERE course_id = %s
            ORDER BY lesson_order ASC, id ASC
            """,
            (course_id,)
        )

    def get_lessons(self, course_id):
        """Get lessons for a course."""

        return self.get_course_lessons(course_id)

    def update_lesson(
        self,
        lesson_id,
        title,
        content,
        video_url=None,
        lesson_order=1
    ):
        """Update a lesson."""

        return self.database.execute(
            """
            UPDATE lessons
            SET title = %s,
                content = %s,
                video_url = %s,
                lesson_order = %s
            WHERE id = %s
            """,
            (title, content, video_url, lesson_order, lesson_id)
        )

    def delete_lesson(self, lesson_id):
        """Delete a lesson."""

        return self.database.execute(
            """
            DELETE FROM lessons
            WHERE id = %s
            """,
            (lesson_id,)
        )

    def create_assignment(
        self,
        course_id,
        title,
        description,
        due_date=None
    ):
        """Create an assignment."""

        course = self.get_course(course_id)

        if course is None:
            return False, "Course not found."

        result = self.database.insert(
            """
            INSERT INTO assignments
                (course_id, title, description, due_date)
            VALUES (%s, %s, %s, %s)
            """,
            (course_id, title, description, due_date)
        )

        if result is None:
            return False, "Unable to create assignment."

        return True, "Assignment created successfully."

    def get_assignment(self, assignment_id):
        """Get one assignment."""

        return self.database.fetch_one(
            """
            SELECT *
            FROM assignments
            WHERE id = %s
            LIMIT 1
            """,
            (assignment_id,)
        )

    def get_course_assignments(self, course_id):
        """Get assignments for a course."""

        return self.database.fetch_all(
            """
            SELECT *
            FROM assignments
            WHERE course_id = %s
            ORDER BY id DESC
            """,
            (course_id,)
        )

    def get_assignments(self, course_id):
        """Get assignments for a course."""

        return self.get_course_assignments(course_id)

    def update_assignment(
        self,
        assignment_id,
        title,
        description,
        due_date=None
    ):
        """Update an assignment."""

        return self.database.execute(
            """
            UPDATE assignments
            SET title = %s,
                description = %s,
                due_date = %s
            WHERE id = %s
            """,
            (title, description, due_date, assignment_id)
        )

    def delete_assignment(self, assignment_id):
        """Delete an assignment."""

        return self.database.execute(
            """
            DELETE FROM assignments
            WHERE id = %s
            """,
            (assignment_id,)
        )


    
    def submit_assignment(self, assignment_id, student_id, answer):
        """Submit a student's answer to an assignment."""

        assignment = self.database.fetch_one(
            """
            SELECT id
            FROM assignments
            WHERE id = %s
            LIMIT 1
            """,
            (assignment_id,)
        )

        if assignment is None:
            return False, "Assignment not found."

        result = self.database.insert(
            """
            INSERT INTO submissions (
                assignment_id,
                user_id,
                submission_text
            )
            VALUES (%s, %s, %s)
            """,
            (assignment_id, student_id, answer)
        )

        if result is None:
            return False, "Unable to submit assignment."

        return True, "Assignment submitted successfully."


    def get_student_submissions(self, student_id):
        """Get all submissions from a student."""

        return self.database.fetch_all(
            """
            SELECT submissions.*,
                   assignments.title AS assignment_title
            FROM submissions
            INNER JOIN assignments
                ON assignments.id = submissions.assignment_id
            WHERE submissions.student_id = %s
            ORDER BY submissions.id DESC
            """,
            (student_id,)
        )

    def get_assignment_submissions(self, assignment_id):
        """Get submissions for an assignment."""

        return self.database.fetch_all(
            """
            SELECT submissions.*,
                   users.first_name,
                   users.last_name,
                   users.email
            FROM submissions
            INNER JOIN users
                ON users.id = submissions.student_id
            WHERE submissions.assignment_id = %s
            ORDER BY submissions.id DESC
            """,
            (assignment_id,)
        )

    def create_quiz(self, course_id, title, description=None):
        """Create a quiz for a course."""

        course = self.get_course(course_id)

        if course is None:
            return False, "Course not found."

        result = self.database.insert(
            """
            INSERT INTO quizzes (course_id, title, description)
            VALUES (%s, %s, %s)
            """,
            (course_id, title, description)
        )

        if result is None:
            return False, "Unable to create quiz."

        return True, "Quiz created successfully."

    def get_quiz(self, quiz_id):
        """Get one quiz by ID."""

        return self.database.fetch_one(
            """
            SELECT *
            FROM quizzes
            WHERE id = %s
            LIMIT 1
            """,
            (quiz_id,)
        )

    def get_course_quizzes(self, course_id):
        """Get all quizzes for a course."""

        return self.database.fetch_all(
            """
            SELECT *
            FROM quizzes
            WHERE course_id = %s
            ORDER BY id DESC
            """,
            (course_id,)
        )

    def get_quizzes(self, course_id=None):
        """Get all quizzes or quizzes for one course."""

        if course_id is None:
            return self.database.fetch_all(
                """
                SELECT *
                FROM quizzes
                ORDER BY id DESC
                """
            )

        return self.get_course_quizzes(course_id)

    def update_quiz(self, quiz_id, title, description=None):
        """Update a quiz."""

        return self.database.execute(
            """
            UPDATE quizzes
            SET title = %s, description = %s
            WHERE id = %s
            """,
            (title, description, quiz_id)
        )

    def delete_quiz(self, quiz_id):
        """Delete a quiz."""

        return self.database.execute(
            """
            DELETE FROM quizzes
            WHERE id = %s
            """,
            (quiz_id,)
        )

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
        """Add a question with the next available order number."""

        quiz = self.get_quiz(quiz_id)

        if quiz is None:
            return False, "Quiz not found."

        correct_answer = str(correct_answer).strip().upper()

        if correct_answer not in ("A", "B", "C", "D"):
            return False, "Correct answer must be A, B, C, or D."

        next_order = self.database.fetch_one(
            """
            SELECT COALESCE(MAX(question_order), 0) + 1 AS next_order
            FROM questions
            WHERE quiz_id = %s
            """,
            (quiz_id,)
        )

        if next_order is None:
            return False, "Unable to determine the question order."

        order_number = next_order["next_order"]

        result = self.database.insert(
            """
            INSERT INTO questions (
                quiz_id,
                question_order,
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                quiz_id,
                order_number,
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer
            )
        )

        if result is None:
            return False, "Unable to create question."

        return True, f"Question {order_number} created successfully."


    def add_question(
        self,
        quiz_id,
        question_text,
        option_a,
        option_b,
        option_c,
        option_d,
        correct_answer
    ):
        """Add a question to a quiz."""

        return self.create_question(
            quiz_id,
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        )

    def get_quiz_questions(self, quiz_id):
        """Get questions for a quiz, including correct answers."""

        return self.database.fetch_all(
            """
            SELECT *
            FROM questions
            WHERE quiz_id = %s
            ORDER BY id ASC
            """,
            (quiz_id,)
        )

    def get_questions(self, quiz_id):
        """Get questions for a quiz."""

        return self.get_quiz_questions(quiz_id)

    def delete_question(self, question_id):
        """Delete a quiz question."""

        return self.database.execute(
            """
            DELETE FROM questions
            WHERE id = %s
            """,
            (question_id,)
        )
    
    def save_quiz_result(self, quiz_id, student_id, score):
        """Save a student's quiz result."""

        quiz = self.get_quiz(quiz_id)

        if quiz is None:
            return False, "Quiz not found."

        student = self.database.fetch_one(
            """
            SELECT id
            FROM users
            WHERE id = %s AND role = 'student'
            LIMIT 1
            """,
            (student_id,)
        )

        if student is None:
            return False, "Student account not found."

        course_id = quiz.get("course_id")

        if course_id is None:
            return False, "The quiz is not linked to a valid course."

        enrollment = self.database.fetch_one(
            """
            SELECT student_id
            FROM enrollments
            WHERE student_id = %s
            AND course_id = %s
            AND status = 'active'
            LIMIT 1
            """,
            (student_id, course_id)
        )

        if enrollment is None:
            return False, "You must be actively enrolled in this course."

        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or score < 0
        ):
            return False, "Invalid quiz score."

        questions = self.get_quiz_questions(quiz_id)
        max_score = len(questions)

        if max_score == 0:
            return False, "This quiz has no questions."

        if score > max_score:
            return False, "The score cannot exceed the total number of questions."

        result = self.database.insert(
            """
            INSERT INTO quiz_results
                (quiz_id, user_id, score, max_score, answers_count)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                quiz_id,
                student_id,
                score,
                max_score,
                max_score
            )
        )

        if result is None:
            return False, "Unable to save quiz result. Check the MySQL error."

        return True, "Quiz result saved successfully."


    def get_student_results(self, student_id):
        """Get a student's quiz results."""

        return self.database.fetch_all(
            """
            SELECT quiz_results.id,
                   quiz_results.quiz_id,
                   quizzes.title,
                   quiz_results.score,
                   quiz_results.max_score,
                   quiz_results.attempted_at
            FROM quiz_results
            INNER JOIN quizzes
                ON quizzes.id = quiz_results.quiz_id
            WHERE quiz_results.user_id = %s
            ORDER BY quiz_results.id DESC
            """,
            (student_id,)
        )

    def get_quiz_results(self, quiz_id):
        """Get results for all students who took a quiz."""

        return self.database.fetch_all(
            """
            SELECT quiz_results.*,
                   users.first_name,
                   users.last_name,
                   users.email
            FROM quiz_results
            INNER JOIN users
                ON users.id = quiz_results.user_id
            WHERE quiz_results.quiz_id = %s
            ORDER BY quiz_results.id DESC
            """,
            (quiz_id,)
        )
