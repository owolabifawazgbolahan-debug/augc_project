from auth import Auth
from email_service import EmailService
from models import LMSModels
from translation_service import TranslationService

class lmsAPP:
    """Console application for the SQI Learning Management System."""

    def __init__(self):
        self.auth = Auth()
        self.email_service = EmailService()
        self.models = LMSModels()
        self.translation_service = TranslationService()
        self.Home()

    #  HOME MENU 

    def Home(self):
        while True:
            print("""
========== SQI LEARNING MANAGEMENT SYSTEM ==========

1. Register
2. Login
3. Create Initial Admin Account
4. Exit


""")

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.Register()
            elif choice == "2":
                self.Login()
            elif choice == "3":
                self.create_admin_account()
            elif choice == "4":
                print("Thank you for using SQI LMS.")
                break
            else:
                print("Invalid choice.")

    # ADMIN ACCOUNT CREATION

    def create_admin_account(self):
        print("\n========== CREATE ADMIN ACCOUNT ==========")

        existing_admin = self.models.database.fetch_one(
            "SELECT id FROM users WHERE role = %s LIMIT 1",
            ("admin",)
        )

        if existing_admin:
            print("An administrator account already exists.")
            return

        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        email = input("Enter admin email: ").strip().lower()
        password = input("Enter admin password: ")
        confirm_password = input("Confirm admin password: ")

        if not first_name or not last_name:
            print("First name and last name are required.")
            return

        if not self.auth.validate_email(email):
            print("Please enter a valid email address.")
            return

        valid, message = self.auth.validate_password(password)

        if not valid:
            print(message)
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        existing_user = self.models.database.fetch_one(
            "SELECT id FROM users WHERE email = %s LIMIT 1",
            (email,)
        )

        if existing_user:
            print("An account with this email already exists.")
            return

        password_hash = self.auth.hash_password(password)

        result = self.models.database.insert(
            """
            INSERT INTO users
                (first_name, last_name, email, password_hash,
                 role, email_verified, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                first_name,
                last_name,
                email,
                password_hash,
                "admin",
                True,
                True
            )
        )

        if result is None:
            print("Failed to create the administrator account.")
        else:
            print("Administrator account created successfully.")
            print("You can now log in with your admin credentials.")

    def Register(self):
        print("\n========== REGISTER ==========")

        first_name = input("Enter your first name: ").strip()
        last_name = input("Enter your last name: ").strip()
        email = input("Enter your email: ").strip().lower()

        print("\nChoose your account type:")
        print("1. Student")
        print("2. Instructor")

        role_choice = input("Enter your choice: ").strip()

        if role_choice == "1":
            role = "student"
        elif role_choice == "2":
            role = "instructor"
        else:
            print("Invalid account type.")
            return

        password = input("Enter your password: ")
        confirm_password = input("Confirm your password: ")

        if password != confirm_password:
            print("Passwords do not match.")
            return

        result = self.auth.register(
            first_name,
            last_name,
            email,
            password,
            role
        )

        if not result[0]:
            print(result[1])
            return

        print(result[1])
        print("Sending your verification code...")

        code = self.email_service.generate_code()

        email_result = self.email_service.send_verification_code(
            email,
            code
        )

        if not email_result[0]:
            print(email_result[1])
            print(
                "Your account exists but remains unverified. "
                "Email verification must be completed before login."
            )
            return

        print(email_result[1])

        while True:
            entered_code = input(
                "Enter the verification code from your email: "
            ).strip()

            verification = self.email_service.verify_code(
                email,
                entered_code
            )

            if not verification[0]:
                print(verification[1])

                if (
                    "expired" in verification[1].lower()
                    or "too many attempts" in verification[1].lower()
                ):
                    return

                continue

            database_result = self.auth.mark_email_verified(email)
            print(database_result[1])

            if database_result[0]:
                print(
                    f"Registration completed! "
                    f"Your account type is {role}."
                )

            return


    def Login(self):
        print("\n========== LOGIN ==========")

        email = input("Enter your email: ").strip()
        password = input("Enter your password: ")

        result = self.auth.login(email, password)

        if not result[0]:
            print(result[1])
            return

        user = result[1]

        print(
            f"\nWelcome {user['first_name']} "
            f"{user['last_name']}!"
        )
        print("Account type:", user["role"])

        if user["role"] == "student":
            self.student_dashboard(user)
        elif user["role"] == "instructor":
            self.instructor_dashboard(user)
        elif user["role"] == "admin":
            self.admin_dashboard(user)
        else:
            print("Unknown account type.")


    def student_dashboard(self, user):
        while True:
            print("""
========== STUDENT DASHBOARD ==========

1. View Available Courses
2. Enroll in a Course
3. View My Courses
4. View Course Lessons
5. View Course Assignments
6. Submit Assignment
7. Take Quiz
8. View My Quiz Results
9. Logout

=======================================
""")

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.view_available_courses()

            elif choice == "2":
                self.enroll_in_course(user)

            elif choice == "3":
                self.view_my_courses(user)

            elif choice == "4":
                course_id = self.select_enrolled_course(user)

                if course_id is not None:
                    lessons = self.models.get_course_lessons(course_id)

                    if not lessons:
                        print("No lessons are available yet.")
                    else:
                        for lesson in lessons:
                            print(
                                f"\nLesson: {lesson['title']}\n"
                                f"{lesson['content']}"
                            )

            elif choice == "5":
                course_id = self.select_enrolled_course(user)

                if course_id is not None:
                    assignments = (
                        self.models.get_course_assignments(course_id)
                    )

                    if not assignments:
                        print("No assignments are available yet.")
                    else:
                        for assignment in assignments:
                            print(
                                f"\nAssignment ID: {assignment['id']}\n"
                                f"Title: {assignment['title']}\n"
                                f"Instructions: "
                                f"{assignment['description']}"
                            )

            elif choice == "6":
                self.submit_assignment(user)

            elif choice == "7":
                self.take_quiz(user)

            elif choice == "8":
                self.view_my_results(user)

            elif choice == "9":
                print("You have logged out.")
                break

            else:
                print("Invalid choice.")


    def view_available_courses(self):
        courses = self.models.get_courses()

        print("\n========== AVAILABLE COURSES ==========")

        if not courses:
            print("No courses are available yet.")
            return

        for course in courses:
            print(f"\nID: {course['id']}")
            print(f"Title: {course['title']}")
            print(f"Description: {course['description']}")


    def enroll_in_course(self, user):
        courses = self.models.get_courses()

        if not courses:
            print("No courses are available.")
            return

        print("\n========== ENROLL IN A COURSE ==========")

        for course in courses:
            print(f"{course['id']}. {course['title']}")

        try:
            course_id = int(input("Enter course ID: ").strip())
        except ValueError:
            print("Enter a valid numeric course ID.")
            return

        course = self.models.get_course(course_id)

        if not course:
            print("Course not found.")
            return

        result = self.models.enroll_student(
            user["id"],
            course_id
        )

        print(result[1])

    def view_my_courses(self, user):
        courses = self.models.get_student_courses(user["id"])

        print("\n========== MY COURSES ==========")

        if not courses:
            print("You have not enrolled in any courses.")
            return

        for course in courses:
            print(f"\nID: {course['id']}")
            print(f"Title: {course['title']}")
            print(f"Description: {course['description']}")

    def select_enrolled_course(self, user):
        courses = self.models.get_student_courses(user["id"])

        if not courses:
            print("You have not enrolled in any courses.")
            return None

        print("\n========== YOUR COURSES ==========")

        for course in courses:
            print(f"{course['id']}. {course['title']}")

        try:
            course_id = int(input("Enter course ID: ").strip())
        except ValueError:
            print("Enter a valid numeric course ID.")
            return None

        for course in courses:
            if int(course["id"]) == course_id:
                return course_id

        print("You are not enrolled in that course.")
        return None


    def submit_assignment(self, user):
        course_id = self.select_enrolled_course(user)

        if course_id is None:
            return

        assignments = self.models.get_course_assignments(course_id)

        if not assignments:
            print("There are no assignments in this course.")
            return

        print("\n========== AVAILABLE ASSIGNMENTS ==========")

        for assignment in assignments:
            print(
                f"\nID: {assignment['id']}\n"
                f"Title: {assignment['title']}\n"
                f"Instructions: {assignment['description']}"
            )

        try:
            assignment_id = int(
                input("\nEnter assignment ID: ").strip()
            )
        except ValueError:
            print("Enter a valid numeric assignment ID.")
            return

        selected_assignment = None

        for assignment in assignments:
            if int(assignment["id"]) == assignment_id:
                selected_assignment = assignment
                break

        if selected_assignment is None:
            print("That assignment does not belong to this course.")
            return

        answer = input("Enter your assignment answer: ").strip()

        if not answer:
            print("Your answer cannot be empty.")
            return

        result = self.models.submit_assignment(
            assignment_id,
            user["id"],
            answer
        )

        print(result[1])


    def take_quiz(self, user):
        course_id = self.select_enrolled_course(user)

        if course_id is None:
            return

        quizzes = self.models.get_course_quizzes(course_id)

        if not quizzes:
            print("No quizzes are available in this course.")
            return

        print("\n========== AVAILABLE QUIZZES ==========")

        for quiz in quizzes:
            print(f"{quiz['id']}. {quiz['title']}")

        try:
            quiz_id = int(input("Enter quiz ID: ").strip())
        except ValueError:
            print("Enter a valid numeric quiz ID.")
            return

        selected_quiz = None

        for quiz in quizzes:
            if int(quiz["id"]) == quiz_id:
                selected_quiz = quiz
                break

        if selected_quiz is None:
            print("That quiz does not belong to this course.")
            return

        questions = self.models.get_quiz_questions(quiz_id)

        if not questions:
            print("This quiz has no questions.")
            return

        score = 0
        total_questions = len(questions)

        print(f"\n========== {selected_quiz['title']} ==========")

        for number, question in enumerate(questions, start=1):
            print(f"\nQuestion {number}: {question['question_text']}")
            print(f"A. {question['option_a']}")
            print(f"B. {question['option_b']}")
            print(f"C. {question['option_c']}")
            print(f"D. {question['option_d']}")

            while True:
                answer = input("Your answer (A/B/C/D): ").strip().upper()

                if answer in ("A", "B", "C", "D"):
                    break

                print("Please enter A, B, C, or D.")

            correct_question = self.models.database.fetch_one(
                """
                SELECT correct_answer
                FROM questions
                WHERE id = %s AND quiz_id = %s
                """,
                (question["id"], quiz_id)
            )

            if (
                correct_question
                and answer == correct_question["correct_answer"].upper()
            ):
                print("Correct!")
                score += 1
            else:
                print("Incorrect.")

        result = self.models.save_quiz_result(
            quiz_id,
            user["id"],
            score
        )

        print("\n========== QUIZ COMPLETED ==========")
        print(f"Correct answers: {score}/{total_questions}")
        print(f"Percentage: {(score / total_questions) * 100:.2f}%")
        print(result[1])


    def view_my_results(self, user):
        results = self.models.get_student_results(user["id"])

        print("\n========== MY QUIZ RESULTS ==========")

        if not results:
            print("You do not have any quiz results yet.")
            return

        for result in results:
            print(f"\nQuiz: {result['title']}")
            print(f"Score: {result['score']}")


    
    def instructor_dashboard(self, user):
        while True:
            print("""
    ========== INSTRUCTOR DASHBOARD ==========

    1. Create Course
    2. View All Courses
    3. Add Lesson
    4. Create Assignment
    5. Create Quiz
    6. Add Quiz Question
    7. Translate Exam Questions
    8. Logout

    """)

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.create_course(user)

            elif choice == "2":
                self.view_available_courses()

            elif choice == "3":
                course_id = self.select_instructor_course(user)

                if course_id is not None:
                    title = input("Enter lesson title: ").strip()
                    content = input("Enter lesson content: ").strip()

                    result = self.models.create_lesson(
                        course_id, title, content
                    )
                    print(result[1])

            elif choice == "4":
                course_id = self.select_instructor_course(user)

                if course_id is not None:
                    title = input("Enter assignment title: ").strip()
                    description = input(
                        "Enter assignment instructions: "
                    ).strip()

                    result = self.models.create_assignment(
                        course_id, title, description
                    )
                    print(result[1])

            elif choice == "5":
                course_id = self.select_instructor_course(user)

                if course_id is not None:
                    title = input("Enter quiz title: ").strip()
                    result = self.models.create_quiz(course_id, title)
                    print(result[1])

            elif choice == "6":
                self.add_quiz_question(user)

            elif choice == "7":
                self.translate_exam_questions(user)

            elif choice == "8":
                print("You have logged out.")
                break

            else:
                print("Invalid choice.")
    
    def create_course(self, user):
        print("\n========== CREATE COURSE ==========")

        title = input("Enter course title: ").strip()
        description = input("Enter course description: ").strip()

        instructor_id = user["id"]

        result = self.models.create_course(
            title,
            description,
            instructor_id
        )

        if result:
            print("Course created successfully!")
            print(f"Course ID: {result}")
        else:
            print("Failed to create course.")

    def select_instructor_course(self, user):
        courses = self.models.get_courses()

        instructor_courses = [
            course for course in courses
            if int(course["instructor_id"]) == int(user["id"])
        ]

        if not instructor_courses:
            print("You have not created any courses yet.")
            return None

        print("\n========== YOUR COURSES ==========")

        for course in instructor_courses:
            print(f"{course['id']}. {course['title']}")

        try:
            course_id = int(input("Enter course ID: ").strip())
        except ValueError:
            print("Enter a valid numeric course ID.")
            return None

        for course in instructor_courses:
            if int(course["id"]) == course_id:
                return course_id

        print("That course does not belong to you.")
        return None


    def add_quiz_question(self, user):
        course_id = self.select_instructor_course(user)

        if course_id is None:
            return

        quizzes = self.models.get_course_quizzes(course_id)

        if not quizzes:
            print("Create a quiz first.")
            return

        print("\n========== AVAILABLE QUIZZES ==========")

        for quiz in quizzes:
            print(f"{quiz['id']}. {quiz['title']}")

        try:
            quiz_id = int(input("Enter quiz ID: ").strip())
        except ValueError:
            print("Enter a valid numeric quiz ID.")
            return

        selected_quiz = None

        for quiz in quizzes:
            if int(quiz["id"]) == quiz_id:
                selected_quiz = quiz
                break

        if selected_quiz is None:
            print("Quiz not found.")
            return

        question_text = input("Enter question: ").strip()
        option_a = input("Option A: ").strip()
        option_b = input("Option B: ").strip()
        option_c = input("Option C: ").strip()
        option_d = input("Option D: ").strip()

        correct_answer = input(
            "Correct answer (A/B/C/D): "
        ).strip().upper()

        result = self.models.create_question(
            quiz_id,
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        )

        print(result[1]),

    
    def translate_exam_questions(self, user):
        """Display quiz questions translated into a chosen language."""

        course_id = self.select_instructor_course(user)

        if course_id is None:
            return

        quizzes = self.models.get_course_quizzes(course_id)

        if not quizzes:
            print("There are no quizzes in this course.")
            return

        print("\n========== SELECT A QUIZ ==========")

        for quiz in quizzes:
            print(f"{quiz['id']}. {quiz['title']}")

        try:
            quiz_id = int(input("Enter quiz ID: ").strip())
        except ValueError:
            print("Enter a valid quiz ID.")
            return

        selected_quiz = None

        for quiz in quizzes:
            if int(quiz["id"]) == quiz_id:
                selected_quiz = quiz
                break

        if selected_quiz is None:
            print("That quiz does not belong to this course.")
            return

        print("""
    ========== SELECT LANGUAGE ==========

    1. Yoruba
    2. Hausa
    3. Igbo
    4. French
    5. Spanish
    6. Arabic
    7. German
    8. Portuguese
    9. Chinese
    10. Hindi
    """)

        languages = {
            "1": "yoruba",
            "2": "hausa",
            "3": "igbo",
            "4": "french",
            "5": "spanish",
            "6": "arabic",
            "7": "german",
            "8": "portuguese",
            "9": "chinese",
            "10": "hindi"
        }

        choice = input("Choose a language: ").strip()
        target_language = languages.get(choice)

        if target_language is None:
            print("Invalid language choice.")
            return

        questions = self.models.get_quiz_questions(quiz_id)

        if not questions:
            print("This quiz has no questions.")
            return

        print(f"\n========== {target_language.upper()} TRANSLATION ==========")
        print("Original questions in the database will not be changed.")

        for number, question in enumerate(questions, start=1):
            print(f"\nQuestion {number}:")

            print(self.translation_service.translate(
                question["question_text"], target_language
            ))

            for option in ("a", "b", "c", "d"):
                option_text = question[f"option_{option}"]

                translated_option = self.translation_service.translate(
                    option_text, target_language
                )

                print(f"{option.upper()}. {translated_option}")

        print("\nTranslation display completed.")


    #ADMIN DASHBOARD

    def admin_dashboard(self, user):
        while True:
            print("""
========== ADMINISTRATOR DASHBOARD ==========

1. View All Users
2. Activate or Deactivate User
3. Promote Student to Instructor
4. View All Courses
5. View System Reports
6. Logout

=============================================
""")

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.admin_view_users()

            elif choice == "2":
                self.admin_toggle_user()

            elif choice == "3":
                self.admin_promote_user()

            elif choice == "4":
                self.view_available_courses()

            elif choice == "5":
                self.admin_view_reports()

            elif choice == "6":
                print("Administrator logged out.")
                break

            else:
                print("Invalid choice.")


    def admin_view_users(self):
        users = self.models.database.fetch_all(
            """
            SELECT id, first_name, last_name, email,
                   role, email_verified, is_active
            FROM users
            ORDER BY id
            """
        )

        print("\n========== REGISTERED USERS ==========")

        if not users:
            print("No users were found.")
            return

        for user in users:
            print(f"\nUser ID: {user['id']}")
            print(
                f"Name: {user['first_name']} "
                f"{user['last_name']}"
            )
            print(f"Email: {user['email']}")
            print(f"Role: {user['role']}")
            print(f"Email verified: {user['email_verified']}")
            print(f"Active: {user['is_active']}")


    def admin_toggle_user(self):
        self.admin_view_users()

        try:
            user_id = int(
                input("\nEnter the user ID to update: ").strip()
            )
        except ValueError:
            print("Enter a valid numeric user ID.")
            return

        target = self.models.database.fetch_one(
            """
            SELECT id, role, is_active
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        if not target:
            print("User not found.")
            return

        if target["role"] == "admin":
            print("Administrator accounts cannot be changed here.")
            return

        new_status = not bool(target["is_active"])

        result = self.models.database.execute(
            "UPDATE users SET is_active = %s WHERE id = %s",
            (new_status, user_id)
        )

        if result is False:
            print("Unable to update the account.")
        else:
            if new_status:
                print("User account activated.")
            else:
                print("User account deactivated.")


    def admin_promote_user(self):
        users = self.models.database.fetch_all(
            """
            SELECT id, first_name, last_name, email
            FROM users
            WHERE role = %s AND is_active = %s
            ORDER BY id
            """,
            ("student", True)
        )

        print("\n========== STUDENTS AVAILABLE FOR PROMOTION ==========")

        if not users:
            print("No active student accounts were found.")
            return

        for student in users:
            print(
                f"\nID: {student['id']}\n"
                f"Name: {student['first_name']} "
                f"{student['last_name']}\n"
                f"Email: {student['email']}"
            )

        try:
            user_id = int(
                input("\nEnter student ID to promote: ").strip()
            )
        except ValueError:
            print("Enter a valid numeric user ID.")
            return

        target = self.models.database.fetch_one(
            """
            SELECT id, role
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        if not target or target["role"] != "student":
            print("The selected user is not a student.")
            return

        result = self.models.database.execute(
            "UPDATE users SET role = %s WHERE id = %s",
            ("instructor", user_id)
        )

        if result is False:
            print("Unable to promote this student.")
        else:
            print("Student promoted to instructor successfully.")


    def admin_view_reports(self):
        print("\n========== SYSTEM REPORTS ==========")

        users = self.models.database.fetch_one(
            """
            SELECT
                COUNT(*) AS total_users,
                SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END)
                    AS total_students,
                SUM(CASE WHEN role = 'instructor' THEN 1 ELSE 0 END)
                    AS total_instructors,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END)
                    AS total_admins
            FROM users
            """
        )

        courses = self.models.database.fetch_one(
            "SELECT COUNT(*) AS total_courses FROM courses"
        )

        enrollments = self.models.database.fetch_one(
            "SELECT COUNT(*) AS total_enrollments FROM enrollments"
        )

        quizzes = self.models.database.fetch_one(
            "SELECT COUNT(*) AS total_quizzes FROM quizzes"
        )

        if users:
            print(f"Total users: {users['total_users'] or 0}")
            print(f"Students: {users['total_students'] or 0}")
            print(f"Instructors: {users['total_instructors'] or 0}")
            print(f"Administrators: {users['total_admins'] or 0}")

        if courses:
            print(f"Total courses: {courses['total_courses'] or 0}")

        if enrollments:
            print(
                f"Total enrollments: "
                f"{enrollments['total_enrollments'] or 0}"
            )

        if quizzes:
            print(f"Total quizzes: {quizzes['total_quizzes'] or 0}")


if __name__ == "__main__":
    app = lmsAPP()
