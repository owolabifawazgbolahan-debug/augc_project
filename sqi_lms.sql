CREATE DATABASE augc_project
USE augc_project;

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'instructor', 'admin')
        NOT NULL DEFAULT 'student',
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_users_role (role),
    INDEX idx_users_active (is_active)
);

CREATE TABLE courses (
    id INT NOT NULL AUTO_INCREMENT,
    instructor_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    duration VARCHAR(50),
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_courses_instructor (instructor_id),
    INDEX idx_courses_published (is_published),

    CONSTRAINT fk_courses_instructor
        FOREIGN KEY (instructor_id)
        REFERENCES users(id)
);



CREATE TABLE enrollments (
    student_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    course_id INT NOT NULL,

    status ENUM('active', 'completed', 'dropped')
        NOT NULL DEFAULT 'active',

    enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    UNIQUE KEY uq_enrollment_user_course (user_id, course_id),
    INDEX idx_enrollments_course (course_id),

    CONSTRAINT fk_enrollments_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),

    CONSTRAINT fk_enrollments_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
);



CREATE TABLE lessons (
    id INT NOT NULL AUTO_INCREMENT,
    course_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    content TEXT,
    video_url VARCHAR(2048),
    lesson_order INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_lesson_order (course_id, lesson_order),
    INDEX idx_lessons_course (course_id),

    CONSTRAINT fk_lessons_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
);

CREATE TABLE assignments (
    id INT NOT NULL AUTO_INCREMENT,
    course_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    due_date DATE,
    max_score DECIMAL(7,2) NOT NULL DEFAULT 100.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_assignments_course (course_id),

    CONSTRAINT chk_assignment_max_score
        CHECK (max_score > 0),

    CONSTRAINT fk_assignments_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
);


CREATE TABLE submissions (
    id INT NOT NULL AUTO_INCREMENT,
    assignment_id INT NOT NULL,
    user_id INT NOT NULL,
    submission_text TEXT,
    submission_file VARCHAR(2048),
    score DECIMAL(7,2) DEFAULT NULL,
    feedback TEXT,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    graded_at TIMESTAMP NULL DEFAULT NULL,

    PRIMARY KEY (id),

    UNIQUE KEY uq_submission_assignment_user (assignment_id, user_id),
    INDEX idx_submissions_user (user_id),

    CONSTRAINT fk_submissions_assignment
        FOREIGN KEY (assignment_id)
        REFERENCES assignments(id),

    CONSTRAINT fk_submissions_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);



CREATE TABLE quizzes (
    id INT NOT NULL AUTO_INCREMENT,
    course_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    total_marks DECIMAL(7,2) NOT NULL DEFAULT 0.00,
    duration_minutes INT NOT NULL DEFAULT 30,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_quizzes_course (course_id),

    CONSTRAINT fk_quizzes_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
);

CREATE TABLE questions (
    id INT NOT NULL AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    question_text TEXT NOT NULL,
    option_a VARCHAR(1000) NOT NULL,
    option_b VARCHAR(1000) NOT NULL,
    option_c VARCHAR(1000) NOT NULL,
    option_d VARCHAR(1000) NOT NULL,
    correct_answer ENUM('A', 'B', 'C', 'D') NOT NULL,
    marks DECIMAL(7,2) NOT NULL DEFAULT 1.00,
    question_order INT UNSIGNED NOT NULL DEFAULT 1,

    PRIMARY KEY (id),
    UNIQUE KEY uq_question_order (quiz_id, question_order),
    INDEX idx_questions_quiz (quiz_id),

    CONSTRAINT fk_questions_quiz
        FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id)
);

CREATE TABLE quiz_results (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    quiz_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    score DECIMAL(7,2) NOT NULL DEFAULT 0.00,
    max_score DECIMAL(7,2) NOT NULL DEFAULT 0.00,
    answers_count INT UNSIGNED NOT NULL DEFAULT 0,
    attempted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_quiz_results_quiz (quiz_id),
    INDEX idx_quiz_results_user (user_id),
    INDEX idx_quiz_results_attempted (attempted_at),

    CONSTRAINT chk_quiz_result_score
        CHECK (score >= 0),

    CONSTRAINT chk_quiz_result_max_score
        CHECK (max_score >= 0),

    CONSTRAINT fk_quiz_results_quiz
        FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id)

    CONSTRAINT fk_quiz_results_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);


CREATE TABLE quiz_results (
    id INT NOT NULL AUTO_INCREMENT,
    quiz_id INT NOT NULL,
    user_id INT NOT NULL,
    score DECIMAL(7,2) NOT NULL DEFAULT 0.00,
    max_score DECIMAL(7,2) NOT NULL DEFAULT 0.00,
    answers_count INT UNSIGNED NOT NULL DEFAULT 0,
    attempted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_quiz_results_user (user_id),
    INDEX idx_quiz_results_quiz (quiz_id),

    CONSTRAINT fk_quiz_results_quiz
        FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id),

    CONSTRAINT fk_quiz_results_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);
