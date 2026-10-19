Learning Management System (LMS)

1. Project Overview

The Learning Management System (LMS) is a Python-based application designed to support online learning and academic management. It uses MySQL to store user accounts, courses, lessons, assignments, quizzes, and student results.

The application provides separate dashboards for students, instructors, and administrators.

2. Technologies Used

- **Programming language:** Python
- **Database:** MySQL
- **Database connector:** mysql-connector-python
- **Password security:** bcrypt
- **Email verification:** SMTP
- **Text-to-speech:** pyttsx3
- **Translation:** deep-translator

3. User Roles

Student
Students can:
- Register and verify their email address.
- Log in to their accounts.
- View available courses.
- Enroll in courses.
- View course lessons and assignments.
- Submit assignment answers.
- Take quizzes.
- View quiz results.

Instructor
Instructors can:
- Register and log in.
- Create courses.
- Add lessons to courses.
- Create assignments.
- Create quizzes.
- Add multiple-choice quiz questions.

Administrator
Administrators can:
- View registered users.
- Activate or deactivate user accounts.
- Promote students to instructors.
- View all courses.
- View system reports.

4. Project Structure

```text
augc_project/
├── lms_app.py
├── lms_config.py
├── database.py
├── models.py
├── auth.py
├── email_service.py
├── voice_assistant.py
├── translation_service.py
├── index.py
├── requirements.txt
├── README.md
├── schema.sql
└── sample_data.sql
```

The file structure above should be adjusted to match the files and folders actually present in the project.

5. Requirements

Before running the application, install:

- Python
- MySQL Server
- pip
- The Python packages listed in `requirements.txt`

6. Installation

Step 1: Open the project folder

Open Anaconda Prompt or PowerShell and navigate to the project directory:

```anaconda prompt
cd C:\augc_project
```

Step 2: Activate the Python environment

```anaconda prompt
scripts\activate augc_project
```

Step 3: Install dependencies

```anaconda prompt
pip install -r requirements.txt
```

7. Database Configuration

The application uses a MySQL database named `augc_project`.

The connection settings used by the project are:

- Host: `127.0.0.1`
- Port: `3306`
- Username: `root`
- Password: blank, if configured that way locally
- Database: `augc_project`

Ensure that MySQL Server is running before starting the application.

Database setup

If the database and tables have not yet been created, run the project's SQL schema file using MySQL Workbench or the MySQL command-line client.

For example:

```sql
CREATE DATABASE IF NOT EXISTS augc_project;
USE augc_project;
```

Create the required tables using the project's actual schema file. Do not recreate existing tables unnecessarily, because doing so may affect stored data.

8. Running the Application

From the project directory, execute:

```anaconda prompt
python lms_app.py
```

Follow the menu displayed in the terminal to register, log in, or access the available features.

9. Authentication and Security

The application includes email verification, password validation, password hashing with bcrypt, and role-based dashboards.

Use a strong password and keep email credentials private. For a production deployment, restrict administrator creation and use appropriate database permissions.

10. Voice Assistant and Translation

The project includes a voice assistant module that uses text-to-speech and a translation module that supports multiple languages.

Translation requires an internet connection and may be affected by external service availability.

11. Testing

Test the following before considering the application complete:

- MySQL connection and table structure.
- Student and instructor registration.
- Email verification and login.
- Course creation and enrollment.
- Lessons and assignment submissions.
- Quiz questions, scoring, and results.
- Administrator account management and reports.

12. Project Status

This project is being developed as a Python and MySQL Learning Management System. Features should be considered complete only after they have been tested successfully.
