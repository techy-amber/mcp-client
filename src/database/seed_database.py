import os
import random
from datetime import datetime

import mysql.connector
from dotenv import load_dotenv


load_dotenv()

# ============================================================
# Configuration
# ============================================================

DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE", "student_ai")

TOTAL_STUDENTS = 5000

# Fixed seed = same synthetic dataset each time
random.seed(42)


# ============================================================
# Synthetic names
# ============================================================

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Krishna",
    "Ishaan", "Rohan", "Rahul", "Kunal", "Aman",
    "Ananya", "Diya", "Riya", "Priya", "Sneha",
    "Isha", "Kavya", "Meera", "Nisha", "Pooja",
    "Aryan", "Harsh", "Yash", "Mohit", "Nikhil",
    "Sakshi", "Neha", "Aditi", "Simran", "Tanvi",
]

LAST_NAMES = [
    "Sharma", "Verma", "Jain", "Gupta", "Singh",
    "Patel", "Agarwal", "Mehta", "Mishra", "Yadav",
    "Joshi", "Shah", "Tiwari", "Chauhan", "Saxena",
]


# ============================================================
# Academic structure
# ============================================================

DEPARTMENTS = [
    ("Computer Science and Engineering", "CSE"),
    ("Artificial Intelligence and Data Science", "AIDS"),
    ("Information Technology", "IT"),
    ("Electronics and Communication Engineering", "ECE"),
]


COURSES = [
    ("B.Tech Computer Science and Engineering", "BTECH-CSE", "CSE"),
    ("B.Tech Artificial Intelligence and Data Science", "BTECH-AIDS", "AIDS"),
    ("B.Tech Information Technology", "BTECH-IT", "IT"),
    (
        "B.Tech Electronics and Communication Engineering",
        "BTECH-ECE",
        "ECE",
    ),
]


# Five subjects per semester for each course.
#
# Code format:
# COURSE-SEMESTER-SUBJECTNUMBER

SUBJECT_NAMES = {
    1: [
        "Engineering Mathematics I",
        "Engineering Physics",
        "Programming Fundamentals",
        "Basic Electrical Engineering",
        "Communication Skills",
    ],
    2: [
        "Engineering Mathematics II",
        "Engineering Chemistry",
        "Object Oriented Programming",
        "Digital Logic",
        "Environmental Studies",
    ],
    3: [
        "Data Structures",
        "Database Management Systems",
        "Discrete Mathematics",
        "Computer Organization",
        "Operating Systems",
    ],
    4: [
        "Design and Analysis of Algorithms",
        "Computer Networks",
        "Software Engineering",
        "Probability and Statistics",
        "Web Technologies",
    ],
    5: [
        "Machine Learning",
        "Theory of Computation",
        "Cloud Computing",
        "Data Analytics",
        "Professional Ethics",
    ],
    6: [
        "Artificial Intelligence",
        "Compiler Design",
        "Distributed Systems",
        "Information Security",
        "Big Data Analytics",
    ],
    7: [
        "Deep Learning",
        "Internet of Things",
        "Natural Language Processing",
        "DevOps",
        "Project Management",
    ],
    8: [
        "Major Project",
        "Industry Internship",
        "Cyber Security",
        "Entrepreneurship",
        "Advanced Computing",
    ],
}


# ============================================================
# Helper functions
# ============================================================

def generate_name():
    return (
        f"{random.choice(FIRST_NAMES)} "
        f"{random.choice(LAST_NAMES)}"
    )


def generate_academic_score():

    """
    Generate realistic-ish student performance.

    Most students are average.
    Some are high performers.
    Some are low performers.
    """

    category = random.choices(
        ["high", "average", "low"],
        weights=[20, 65, 15],
        k=1,
    )[0]

    if category == "high":
        return random.uniform(75, 96)

    if category == "low":
        return random.uniform(35, 60)

    return random.uniform(55, 80)


def generate_attendance(score):

    """
    Attendance has a loose relationship with performance,
    while still containing randomness.
    """

    base = 55 + (score * 0.35)

    attendance = random.gauss(base, 8)

    return max(
        40,
        min(100, attendance),
    )


# ============================================================
# Main seeding function
# ============================================================

def seed_database():

    connection = None
    cursor = None

    try:

        # ====================================================
        # Connect
        # ====================================================

        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )

        cursor = connection.cursor()

        print("Connected to student_ai database.")

        # ====================================================
        # Clear existing synthetic data
        # ====================================================

        print("\nClearing existing data...")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        cursor.execute("TRUNCATE TABLE attendance")
        cursor.execute("TRUNCATE TABLE marks")
        cursor.execute("TRUNCATE TABLE students")
        cursor.execute("TRUNCATE TABLE subjects")
        cursor.execute("TRUNCATE TABLE courses")
        cursor.execute("TRUNCATE TABLE departments")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        connection.commit()

        # ====================================================
        # Insert departments
        # ====================================================

        print("Creating departments...")

        cursor.executemany(
            """
            INSERT INTO departments (
                department_name,
                department_code
            )
            VALUES (%s, %s)
            """,
            DEPARTMENTS,
        )

        connection.commit()

        cursor.execute(
            """
            SELECT department_id, department_code
            FROM departments
            """
        )

        department_ids = {
            code: department_id
            for department_id, code in cursor.fetchall()
        }

        # ====================================================
        # Insert courses
        # ====================================================

        print("Creating courses...")

        course_rows = []

        for course_name, course_code, department_code in COURSES:

            course_rows.append(
                (
                    course_name,
                    course_code,
                    department_ids[department_code],
                    8,
                )
            )

        cursor.executemany(
            """
            INSERT INTO courses (
                course_name,
                course_code,
                department_id,
                duration_semesters
            )
            VALUES (%s, %s, %s, %s)
            """,
            course_rows,
        )

        connection.commit()

        cursor.execute(
            """
            SELECT course_id, course_code
            FROM courses
            """
        )

        course_ids = {
            code: course_id
            for course_id, code in cursor.fetchall()
        }

        # ====================================================
        # Insert subjects
        # ====================================================

        print("Creating subjects...")

        subject_rows = []

        for _, course_code, _ in COURSES:

            short_code = course_code.replace("BTECH-", "")

            for semester in range(1, 9):

                names = SUBJECT_NAMES[semester]

                for number, subject_name in enumerate(
                    names,
                    start=1,
                ):

                    subject_code = (
                        f"{short_code}-"
                        f"{semester}0{number}"
                    )

                    subject_rows.append(
                        (
                            subject_code,
                            subject_name,
                            course_ids[course_code],
                            semester,
                            4,
                        )
                    )

        cursor.executemany(
            """
            INSERT INTO subjects (
                subject_code,
                subject_name,
                course_id,
                semester,
                credits
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            subject_rows,
        )

        connection.commit()

        # ====================================================
        # Cache subjects by course + semester
        # ====================================================

        cursor.execute(
            """
            SELECT
                subject_id,
                course_id,
                semester
            FROM subjects
            """
        )

        subjects_by_course_semester = {}

        for subject_id, course_id, semester in cursor.fetchall():

            key = (course_id, semester)

            subjects_by_course_semester.setdefault(
                key,
                [],
            ).append(subject_id)

        # ====================================================
        # Generate students
        # ====================================================

        print(
            f"Generating {TOTAL_STUDENTS:,} students..."
        )

        student_rows = []

        # Keep each student's underlying performance profile.
        student_profiles = {}

        current_year = datetime.now().year

        available_courses = list(course_ids.items())

        for index in range(TOTAL_STUDENTS):

            student_id = 100001 + index

            name = generate_name()

            course_code, course_id = random.choice(
                available_courses
            )

            semester = random.randint(1, 8)

            section = random.choice(
                ["A", "B", "C", "D"]
            )

            # Approximate admission year from current semester.
            academic_year_offset = (semester - 1) // 2

            admission_year = (
                current_year - academic_year_offset
            )

            enrollment_number = (
                f"STU{student_id}"
            )

            email = (
                f"student{student_id}@college.edu"
            )

            student_rows.append(
                (
                    student_id,
                    enrollment_number,
                    name,
                    email,
                    course_id,
                    semester,
                    section,
                    admission_year,
                )
            )

            student_profiles[student_id] = (
                generate_academic_score()
            )

        cursor.executemany(
            """
            INSERT INTO students (
                student_id,
                enrollment_number,
                name,
                email,
                course_id,
                semester,
                section,
                admission_year
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            student_rows,
        )

        connection.commit()

        print("Students inserted.")

        # ====================================================
        # Generate marks and attendance
        # ====================================================

        print("Generating marks and attendance...")

        marks_rows = []
        attendance_rows = []

        exam_structure = [
            ("MIDTERM", 30),
            ("ENDTERM", 100),
            ("ASSIGNMENT", 20),
            ("PRACTICAL", 50),
        ]

        # Need course and semester for every student
        cursor.execute(
            """
            SELECT
                student_id,
                course_id,
                semester
            FROM students
            """
        )

        students = cursor.fetchall()

        for student_id, course_id, semester in students:

            profile_score = student_profiles[
                student_id
            ]

            subject_ids = (
                subjects_by_course_semester[
                    (course_id, semester)
                ]
            )

            for subject_id in subject_ids:

                # Each subject gets some variation.
                subject_score = max(
                    20,
                    min(
                        98,
                        random.gauss(
                            profile_score,
                            8,
                        ),
                    ),
                )

                # ============================================
                # Marks
                # ============================================

                for exam_type, max_marks in exam_structure:

                    percentage = max(
                        0,
                        min(
                            100,
                            random.gauss(
                                subject_score,
                                6,
                            ),
                        ),
                    )

                    marks_obtained = round(
                        max_marks * percentage / 100,
                        2,
                    )

                    marks_rows.append(
                        (
                            student_id,
                            subject_id,
                            exam_type,
                            marks_obtained,
                            max_marks,
                        )
                    )

                # ============================================
                # Attendance
                # ============================================

                total_classes = random.randint(
                    45,
                    70,
                )

                attendance_percentage = (
                    generate_attendance(
                        subject_score
                    )
                )

                classes_attended = round(
                    total_classes
                    * attendance_percentage
                    / 100
                )

                classes_attended = min(
                    classes_attended,
                    total_classes,
                )

                attendance_rows.append(
                    (
                        student_id,
                        subject_id,
                        classes_attended,
                        total_classes,
                    )
                )

        # ====================================================
        # Bulk insert marks
        # ====================================================

        print(
            f"Inserting {len(marks_rows):,} mark records..."
        )

        cursor.executemany(
            """
            INSERT INTO marks (
                student_id,
                subject_id,
                exam_type,
                marks_obtained,
                max_marks
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            marks_rows,
        )

        connection.commit()

        # ====================================================
        # Bulk insert attendance
        # ====================================================

        print(
            f"Inserting "
            f"{len(attendance_rows):,} "
            f"attendance records..."
        )

        cursor.executemany(
            """
            INSERT INTO attendance (
                student_id,
                subject_id,
                classes_attended,
                total_classes
            )
            VALUES (%s, %s, %s, %s)
            """,
            attendance_rows,
        )

        connection.commit()

        # ====================================================
        # Verification
        # ====================================================

        print("\nVerifying database...")

        tables = [
            "departments",
            "courses",
            "subjects",
            "students",
            "marks",
            "attendance",
        ]

        print("\nRecord counts:")

        for table in tables:

            cursor.execute(
                f"SELECT COUNT(*) FROM `{table}`"
            )

            count = cursor.fetchone()[0]

            print(
                f"{table:<15} {count:,}"
            )

        print("\n====================================")
        print("Database seeded successfully!")
        print("====================================")

    except mysql.connector.Error as error:

        print("\nMySQL error:")
        print(error)

        if connection:
            connection.rollback()

    except Exception as error:

        print("\nUnexpected error:")
        print(error)

        if connection:
            connection.rollback()

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            if connection.is_connected():
                connection.close()

        print("\nMySQL connection closed.")


if __name__ == "__main__":
    seed_database()