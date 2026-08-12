from services.student_service import StudentService

from mcp.server import MCPServer

from database.db import get_connection


# ============================================================
# Student MCP Server
# ============================================================
student_service = StudentService()
mcp = MCPServer("Student Server")


# ============================================================
# Helper functions
# ============================================================

def clamp_limit(limit: int, maximum: int = 100) -> int:
    """Keep result sizes safe for the LLM context."""
    return max(1, min(int(limit), maximum))


def to_float(value):
    """Convert MySQL Decimal values into JSON-friendly floats."""
    return None if value is None else float(value)


# ============================================================
# Tool 1: Get student
# ============================================================

@mcp.tool()
def get_student(student_id: int) -> dict:
    """Get basic information about a student."""

    return student_service.get_student(student_id)

    


# ============================================================
# Tool 2: Get student marks
# ============================================================

@mcp.tool()
def get_student_marks(student_id: int) -> dict:
    """Get subject-wise exam marks for a student."""

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    


# ============================================================
# Tool 3: Calculate average
# ============================================================

@mcp.tool()
def calculate_average(student_id: int) -> dict:
      return student_service.calculate_average(student_id)

    


# ============================================================
# Tool 4: Weakest subject
# ============================================================
@mcp.tool()
def get_weakest_subject(student_id: int) -> dict:
    return student_service.get_weakest_subject(student_id)

# ============================================================
# Tool 5: Student attendance
# ============================================================

@mcp.tool()
def get_student_attendance(student_id: int) -> dict:
    return student_service.get_student_attendance(student_id)


# ============================================================
# Tool 6: Find at-risk students
# ============================================================

@mcp.tool()
def find_at_risk_students(
    attendance_threshold: float = 75.0,
    marks_threshold: float = 60.0,
    limit: int = 20,
) -> dict:
    return student_service.find_at_risk_students(
        attendance_threshold,
        marks_threshold,
        limit,
    )

# ============================================================
# Tool 7: Find top students
# ============================================================

@mcp.tool()
def find_top_students(
    limit: int = 10,
    course_code: str = "",
    semester: int = 0,
) -> dict:
    return student_service.find_top_students(
        limit,
        course_code,
        semester,
    )

# ============================================================
# Tool 8: Find low-attendance students
# ============================================================

@mcp.tool()
def find_low_attendance_students(
    threshold: float = 75.0,
    limit: int = 20,
) -> dict:
    return student_service.find_low_attendance_students(
        threshold,
        limit,
    )


# ============================================================
# Tool 9: Subject performance
# ============================================================

@mcp.tool()
def get_subject_performance(
    subject_code: str,
) -> dict:
    return student_service.get_subject_performance(
        subject_code
    )


# ============================================================
# Tool 10: Course performance
# ============================================================

@mcp.tool()
def get_course_performance(
    course_code: str,
) -> dict:
    return student_service.get_course_performance(
        course_code
    )
# ============================================================
# Tool 11: Semester performance
# ============================================================

@mcp.tool()
def get_semester_performance(
    course_code: str,
    semester: int,
) -> dict:
    return student_service.get_semester_performance(
        course_code,
        semester,
    )

# ============================================================
# Tool 12: Compare students
# ============================================================

@mcp.tool()
def compare_students(
    student_ids: list[int],
) -> dict:
    return student_service.compare_students(
        student_ids
    )

# ============================================================
# Tool 13: Class statistics
# ============================================================

@mcp.tool()
def get_class_statistics(
    course_code: str,
    semester: int,
    section: str = "",
) -> dict:
    return student_service.get_class_statistics(
        course_code,
        semester,
        section,
    )


# ============================================================
# Tool 14: Find weak subjects
# ============================================================
@mcp.tool()
def find_weak_subjects(
    course_code: str,
    semester: int,
    limit: int = 5,
) -> dict:
    return student_service.find_weak_subjects(
        course_code,
        semester,
        limit,
    )


# ============================================================
# Tool 15: Student risk score
# ============================================================

@mcp.tool()
def get_student_risk_score(
    student_id: int,
) -> dict:
    return student_service.get_student_risk_score(
        student_id
    )

# ============================================================
# Tool 16: Find highest-risk students
# ============================================================

@mcp.tool()
def find_high_risk_students(
    limit: int = 10,
) -> dict:
    return student_service.find_high_risk_students(
        limit
    )
# ============================================================
# Tool 17: Search students
# ============================================================

@mcp.tool()
def search_students(
    search_term: str,
    limit: int = 10,
) -> dict:
    return student_service.search_students(
        search_term,
        limit,
    )

# ============================================================
# Tool 18: Database summary
# ============================================================

@mcp.tool()
def get_database_summary() -> dict:
    return student_service.get_database_summary()