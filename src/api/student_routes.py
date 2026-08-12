from fastapi import APIRouter, Query
from services.student_service import StudentService

router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

student_service = StudentService()

@router.get("/search")
def search_students(
    search_term: str,
    limit: int = 10,
):
    return student_service.search_students(
        search_term,
        limit,
    )

@router.get("/compare")
def compare_students(
    student_ids: list[int] = Query(...),
):
    return student_service.compare_students(
        student_ids
    )

@router.get("/top")
def find_top_students(
    limit: int = 10,
    course_code: str = "",
    semester: int = 0,
):
    return student_service.find_top_students(
        limit,
        course_code,
        semester,
    )

@router.get("/at-risk")
def find_at_risk_students(
    attendance_threshold: float = 75.0,
    marks_threshold: float = 60.0,
    limit: int = 20,
):
    return student_service.find_at_risk_students(
        attendance_threshold,
        marks_threshold,
        limit,
    )


@router.get("/high-risk")
def find_high_risk_students(
    limit: int = 10,
):
    return student_service.find_high_risk_students(
        limit
    )

@router.get("/low-attendance")
def find_low_attendance_students(
    threshold: float = 75.0,
    limit: int = 20,
):
    return student_service.find_low_attendance_students(
        threshold,
        limit,
    )

@router.get("/database-summary")
def get_database_summary():
    return student_service.get_database_summary()

@router.get("/course-performance")
def get_course_performance(
    course_code: str,
):
    return student_service.get_course_performance(
        course_code
    )


@router.get("/semester-performance")
def get_semester_performance(
    course_code: str,
    semester: int,
):
    return student_service.get_semester_performance(
        course_code,
        semester,
    )

@router.get("/class-statistics")
def get_class_statistics(
    course_code: str,
    semester: int,
    section: str = "",
):
    return student_service.get_class_statistics(
        course_code,
        semester,
        section,
    )


@router.get("/weak-subjects")
def find_weak_subjects(
    course_code: str,
    semester: int,
    limit: int = 5,
):
    return student_service.find_weak_subjects(
        course_code,
        semester,
        limit,
    )

@router.get("/subject-performance")
def get_subject_performance(
    subject_code: str,
):
    return student_service.get_subject_performance(
        subject_code
    )




@router.get("/{student_id}/marks")
def get_student_marks(student_id: int):
    return student_service.get_student_marks(student_id)


@router.get("/{student_id}/attendance")
def get_student_attendance(student_id: int):
    return student_service.get_student_attendance(student_id)


@router.get("/{student_id}/average")
def calculate_average(student_id: int):
    return student_service.calculate_average(student_id)


@router.get("/{student_id}/weakest-subject")
def get_weakest_subject(student_id: int):
    return student_service.get_weakest_subject(student_id)


@router.get("/{student_id}/risk")
def get_student_risk_score(student_id: int):
    return student_service.get_student_risk_score(student_id)


@router.get("/{student_id}")
def get_student(student_id: int):
    return student_service.get_student(student_id)




















