import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# Database configuration
# ============================================================

DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE", "student_ai")


def create_schema():

    connection = None
    cursor = None

    try:

        # ====================================================
        # 1. Connect to MySQL Server
        # ====================================================

        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
        )

        cursor = connection.cursor()

        print("Connected to MySQL.")

        # ====================================================
        # 2. Create database
        # ====================================================

        cursor.execute(
            f"""
            CREATE DATABASE IF NOT EXISTS `{DB_NAME}`
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
            """
        )

        print(f"Database '{DB_NAME}' ready.")

        cursor.execute(f"USE `{DB_NAME}`")

        # ====================================================
        # 3. Departments
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS departments (
                department_id INT AUTO_INCREMENT PRIMARY KEY,

                department_name VARCHAR(100)
                    NOT NULL UNIQUE,

                department_code VARCHAR(20)
                    NOT NULL UNIQUE
            )
            """
        )

        print("Table ready: departments")

        # ====================================================
        # 4. Courses
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id INT AUTO_INCREMENT PRIMARY KEY,

                course_name VARCHAR(100)
                    NOT NULL,

                course_code VARCHAR(30)
                    NOT NULL UNIQUE,

                department_id INT
                    NOT NULL,

                duration_semesters INT
                    NOT NULL DEFAULT 8,

                CONSTRAINT fk_course_department
                    FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
            )
            """
        )

        print("Table ready: courses")

        # ====================================================
        # 5. Students
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INT PRIMARY KEY,

                enrollment_number VARCHAR(30)
                    NOT NULL UNIQUE,

                name VARCHAR(100)
                    NOT NULL,

                email VARCHAR(150)
                    NOT NULL UNIQUE,

                course_id INT
                    NOT NULL,

                semester INT
                    NOT NULL,

                section VARCHAR(10)
                    NOT NULL,

                admission_year INT
                    NOT NULL,

                CONSTRAINT fk_student_course
                    FOREIGN KEY (course_id)
                    REFERENCES courses(course_id),

                INDEX idx_student_course_semester
                    (course_id, semester),

                INDEX idx_student_name
                    (name)
            )
            """
        )

        print("Table ready: students")

        # ====================================================
        # 6. Subjects
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INT AUTO_INCREMENT PRIMARY KEY,

                subject_code VARCHAR(30)
                    NOT NULL UNIQUE,

                subject_name VARCHAR(120)
                    NOT NULL,

                course_id INT
                    NOT NULL,

                semester INT
                    NOT NULL,

                credits INT
                    NOT NULL DEFAULT 4,

                CONSTRAINT fk_subject_course
                    FOREIGN KEY (course_id)
                    REFERENCES courses(course_id),

                INDEX idx_subject_course_semester
                    (course_id, semester)
            )
            """
        )

        print("Table ready: subjects")

        # ====================================================
        # 7. Marks
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS marks (
                mark_id BIGINT AUTO_INCREMENT PRIMARY KEY,

                student_id INT
                    NOT NULL,

                subject_id INT
                    NOT NULL,

                exam_type ENUM(
                    'MIDTERM',
                    'ENDTERM',
                    'ASSIGNMENT',
                    'PRACTICAL'
                ) NOT NULL,

                marks_obtained DECIMAL(5,2)
                    NOT NULL,

                max_marks DECIMAL(5,2)
                    NOT NULL,

                CONSTRAINT fk_marks_student
                    FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_marks_subject
                    FOREIGN KEY (subject_id)
                    REFERENCES subjects(subject_id)
                    ON DELETE CASCADE,

                CONSTRAINT chk_marks_nonnegative
                    CHECK (marks_obtained >= 0),

                CONSTRAINT chk_max_marks_positive
                    CHECK (max_marks > 0),

                CONSTRAINT chk_marks_within_max
                    CHECK (marks_obtained <= max_marks),

                UNIQUE KEY uq_student_subject_exam (
                    student_id,
                    subject_id,
                    exam_type
                ),

                INDEX idx_marks_student
                    (student_id),

                INDEX idx_marks_subject
                    (subject_id)
            )
            """
        )

        print("Table ready: marks")

        # ====================================================
        # 8. Attendance
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id BIGINT AUTO_INCREMENT PRIMARY KEY,

                student_id INT
                    NOT NULL,

                subject_id INT
                    NOT NULL,

                classes_attended INT
                    NOT NULL,

                total_classes INT
                    NOT NULL,

                CONSTRAINT fk_attendance_student
                    FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_attendance_subject
                    FOREIGN KEY (subject_id)
                    REFERENCES subjects(subject_id)
                    ON DELETE CASCADE,

                CONSTRAINT chk_classes_attended
                    CHECK (classes_attended >= 0),

                CONSTRAINT chk_total_classes
                    CHECK (total_classes > 0),

                CONSTRAINT chk_attendance_valid
                    CHECK (classes_attended <= total_classes),

                UNIQUE KEY uq_student_subject_attendance (
                    student_id,
                    subject_id
                ),

                INDEX idx_attendance_student
                    (student_id),

                INDEX idx_attendance_subject
                    (subject_id)
            )
            """
        )

        print("Table ready: attendance")

        connection.commit()

        print("\n================================")
        print("Student AI schema created!")
        print("================================")

    except mysql.connector.Error as error:

        print("\nMySQL error:")
        print(error)

        if connection:
            connection.rollback()

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

        print("\nMySQL connection closed.")


if __name__ == "__main__":
    create_schema()