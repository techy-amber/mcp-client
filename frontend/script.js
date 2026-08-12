const API_BASE = "https://mcp-client-ncph.onrender.com";


// ============================================================
// RISK BADGE
// ============================================================

function getRiskBadge(riskLevel) {

    const level = String(riskLevel || "").toLowerCase();

    let className = "risk-medium";

    if (level === "low") {
        className = "risk-low";
    }

    if (level === "high") {
        className = "risk-high";
    }

    return `
        <span class="risk-badge ${className}">
            ${riskLevel || "-"}
        </span>
    `;
}


// ============================================================
// LOAD DASHBOARD
// ============================================================

async function loadDashboard() {

    try {

        const response = await fetch(
            `${API_BASE}/students/database-summary`
        );

        if (!response.ok) {
            throw new Error("Failed to load dashboard");
        }

        const data = await response.json();

        document.getElementById("totalStudents").textContent =
            data.total_students ?? "-";

        document.getElementById("totalCourses").textContent =
            data.total_courses ?? "-";

        document.getElementById("averageMarks").textContent =
            data.institution_average != null
                ? `${data.institution_average}%`
                : "-";

        document.getElementById("averageAttendance").textContent =
            data.institution_attendance != null
                ? `${data.institution_attendance}%`
                : "-";

    } catch (error) {

        console.error("Dashboard error:", error);

    }
}


// ============================================================
// SEARCH STUDENT
// ============================================================

async function searchStudent() {

    const searchTerm =
        document.getElementById("searchInput").value.trim();

    const resultDiv =
        document.getElementById("searchResults");


    if (!searchTerm) {

        resultDiv.innerHTML = `
            <p class="muted">
                Please enter a student name or enrollment number.
            </p>
        `;

        return;
    }


    resultDiv.innerHTML = `
        <p class="muted">
            Searching...
        </p>
    `;


    try {

        const response = await fetch(
            `${API_BASE}/students/search?search_term=${encodeURIComponent(searchTerm)}`
        );


        if (!response.ok) {
            throw new Error("Search failed");
        }


        const data = await response.json();


        if (!data.students || data.students.length === 0) {

            resultDiv.innerHTML = `
                <p class="muted">
                    No students found.
                </p>
            `;

            return;
        }


        resultDiv.innerHTML = data.students.map(student => `

            <div class="student-result">

                <h3>
                    ${student.name}
                </h3>

                <div class="student-info">

                    <div>
                        <strong>Student ID:</strong>
                        ${student.student_id}
                    </div>

                    <div>
                        <strong>Enrollment:</strong>
                        ${student.enrollment_number}
                    </div>

                    <div>
                        <strong>Course:</strong>
                        ${student.course_code}
                    </div>

                    <div>
                        <strong>Semester:</strong>
                        ${student.semester}
                    </div>

                    <div>
                        <strong>Section:</strong>
                        ${student.section}
                    </div>

                    <div>
                        <strong>Email:</strong>
                        ${student.email ?? "-"}
                    </div>

                </div>

                <br>

                <button
                    onclick="viewStudentDetails(${student.student_id})"
                >
                    View Details
                </button>

            </div>

        `).join("");


    } catch (error) {

        console.error("Search error:", error);

        resultDiv.innerHTML = `
            <p class="muted">
                Unable to connect to backend.
            </p>
        `;

    }
}


// ============================================================
// STUDENT DETAILS
// ============================================================

async function viewStudentDetails(studentId) {

    const resultDiv =
        document.getElementById("searchResults");


    resultDiv.innerHTML = `
        <p class="muted">
            Loading student details...
        </p>
    `;


    try {

        const [
            studentResponse,
            marksResponse,
            attendanceResponse,
            averageResponse,
            riskResponse
        ] = await Promise.all([

            fetch(
                `${API_BASE}/students/${studentId}`
            ),

            fetch(
                `${API_BASE}/students/${studentId}/marks`
            ),

            fetch(
                `${API_BASE}/students/${studentId}/attendance`
            ),

            fetch(
                `${API_BASE}/students/${studentId}/average`
            ),

            fetch(
                `${API_BASE}/students/${studentId}/risk`
            )

        ]);


        if (!studentResponse.ok) {
            throw new Error("Failed to load student");
        }

        if (!marksResponse.ok) {
            throw new Error("Failed to load marks");
        }

        if (!attendanceResponse.ok) {
            throw new Error("Failed to load attendance");
        }

        if (!averageResponse.ok) {
            throw new Error("Failed to load average");
        }

        if (!riskResponse.ok) {
            throw new Error("Failed to load risk");
        }


        const student =
            await studentResponse.json();

        const marks =
            await marksResponse.json();

        const attendance =
            await attendanceResponse.json();

        const average =
            await averageResponse.json();

        const risk =
            await riskResponse.json();


        // ====================================================
        // MARKS TABLE
        // ====================================================

        let marksHTML = "";

        const subjects =
            marks.subjects || {};

        const subjectNames =
            Object.keys(subjects);


        if (subjectNames.length === 0) {

            marksHTML = `
                <tr>
                    <td colspan="5">
                        No subject marks available.
                    </td>
                </tr>
            `;

        } else {

            marksHTML = subjectNames.map(
                subjectName => {

                    const subject =
                        subjects[subjectName];

                    const exams =
                        subject.exams || {};


                    let obtained = 0;
                    let maximum = 0;


                    Object.values(exams).forEach(
                        exam => {

                            obtained += Number(
                                exam.marks_obtained || 0
                            );

                            maximum += Number(
                                exam.max_marks || 0
                            );

                        }
                    );


                    const percentage =
                        maximum > 0
                            ? (
                                obtained /
                                maximum *
                                100
                            ).toFixed(2)
                            : "-";


                    return `

                        <tr>

                            <td>
                                ${subject.subject_code || "-"}
                            </td>

                            <td>
                                ${subjectName}
                            </td>

                            <td>
                                ${obtained.toFixed(2)}
                            </td>

                            <td>
                                ${maximum.toFixed(2)}
                            </td>

                            <td>
                                ${percentage}%
                            </td>

                        </tr>

                    `;

                }
            ).join("");

        }


        // ====================================================
        // ATTENDANCE TABLE
        // ====================================================

        let attendanceHTML = "";

        const attendanceSubjects =
            attendance.subjects || [];


        if (attendanceSubjects.length === 0) {

            attendanceHTML = `
                <tr>
                    <td colspan="5">
                        No attendance data available.
                    </td>
                </tr>
            `;

        } else {

            attendanceHTML =
                attendanceSubjects.map(
                    subject => `

                        <tr>

                            <td>
                                ${subject.subject_code || "-"}
                            </td>

                            <td>
                                ${subject.subject || "-"}
                            </td>

                            <td>
                                ${subject.classes_attended ?? "-"}
                            </td>

                            <td>
                                ${subject.total_classes ?? "-"}
                            </td>

                            <td>
                                ${subject.attendance_percentage ?? "-"}%
                            </td>

                        </tr>

                    `
                ).join("");

        }


        // ====================================================
        // DISPLAY STUDENT
        // ====================================================

        resultDiv.innerHTML = `

            <div class="student-result">

                <h2>
                    ${student.name || "Student"}
                </h2>


                <div class="student-info">

                    <div>
                        <strong>Student ID:</strong>
                        ${student.student_id ?? "-"}
                    </div>

                    <div>
                        <strong>Enrollment:</strong>
                        ${student.enrollment_number ?? "-"}
                    </div>

                    <div>
                        <strong>Course:</strong>
                        ${student.course_code ?? "-"}
                    </div>

                    <div>
                        <strong>Semester:</strong>
                        ${student.semester ?? "-"}
                    </div>

                    <div>
                        <strong>Section:</strong>
                        ${student.section ?? "-"}
                    </div>

                    <div>
                        <strong>Email:</strong>
                        ${student.email ?? "-"}
                    </div>

                </div>


                <br>

                <hr>

                <br>


                <h3>
                    Academic Performance
                </h3>

                <br>


                <div class="student-info">

                    <div>
                        <strong>Average Marks:</strong>
                        ${average.average ?? "-"}%
                    </div>

                    <div>
                        <strong>Attendance:</strong>
                        ${attendance.overall_attendance ?? "-"}%
                    </div>

                    <div>
                        <strong>Risk Score:</strong>
                        ${risk.risk_score ?? "-"}
                    </div>

                    <div>
                        <strong>Risk Level:</strong>
                        ${getRiskBadge(risk.risk_level)}
                    </div>

                </div>


                <br>

                <hr>

                <br>


                <h3>
                    Subject-wise Marks
                </h3>

                <br>


                <table>

                    <thead>

                        <tr>

                            <th>Subject Code</th>
                            <th>Subject</th>
                            <th>Marks Obtained</th>
                            <th>Maximum Marks</th>
                            <th>Percentage</th>

                        </tr>

                    </thead>

                    <tbody>

                        ${marksHTML}

                    </tbody>

                </table>


                <br>

                <hr>

                <br>


                <h3>
                    Subject-wise Attendance
                </h3>

                <br>


                <table>

                    <thead>

                        <tr>

                            <th>Subject Code</th>
                            <th>Subject</th>
                            <th>Classes Attended</th>
                            <th>Total Classes</th>
                            <th>Attendance</th>

                        </tr>

                    </thead>

                    <tbody>

                        ${attendanceHTML}

                    </tbody>

                </table>


                <br>


                <button
                    onclick="searchStudent()"
                >
                    Back to Search
                </button>

            </div>

        `;


    } catch (error) {

        console.error(
            "Student details error:",
            error
        );


        resultDiv.innerHTML = `

            <p class="muted">
                Unable to load student details.
            </p>

            <br>

            <button
                onclick="searchStudent()"
            >
                Back to Search
            </button>

        `;

    }
}


// ============================================================
// COMPARE STUDENTS
// ============================================================

async function compareStudents() {

    const student1 =
        document.getElementById(
            "compareStudent1"
        ).value.trim();

    const student2 =
        document.getElementById(
            "compareStudent2"
        ).value.trim();

    const student3 =
        document.getElementById(
            "compareStudent3"
        ).value.trim();


    const resultDiv =
        document.getElementById(
            "comparisonResults"
        );


    const studentIds = [
        student1,
        student2,
        student3
    ]
        .filter(id => id !== "")
        .map(id => Number(id));


    if (studentIds.length < 2) {

        resultDiv.innerHTML = `
            <p class="muted">
                Please enter at least two student IDs.
            </p>
        `;

        return;
    }


    const uniqueIds =
        [...new Set(studentIds)];


    if (uniqueIds.length < 2) {

        resultDiv.innerHTML = `
            <p class="muted">
                Please enter different student IDs.
            </p>
        `;

        return;
    }


    resultDiv.innerHTML = `
        <p class="muted">
            Comparing students...
        </p>
    `;


    try {

        const params =
            uniqueIds
                .map(
                    id => `student_ids=${id}`
                )
                .join("&");


        const response = await fetch(
            `${API_BASE}/students/compare?${params}`
        );


        if (!response.ok) {
            throw new Error(
                "Comparison failed"
            );
        }


        const data =
            await response.json();


        if (
            !data.comparison ||
            data.comparison.length === 0
        ) {

            resultDiv.innerHTML = `
                <p class="muted">
                    No matching students found.
                </p>
            `;

            return;
        }


        const rows =
            data.comparison.map(
                (student, index) => `

                    <tr>

                        <td>
                            ${index + 1}
                        </td>

                        <td>
                            ${student.student_id}
                        </td>

                        <td>
                            ${student.name}
                        </td>

                        <td>
                            ${student.course_code}
                        </td>

                        <td>
                            ${student.semester}
                        </td>

                        <td>
                            ${student.average_marks ?? "-"}%
                        </td>

                        <td>
                            ${student.attendance_percentage ?? "-"}%
                        </td>

                    </tr>

                `
            ).join("");


        resultDiv.innerHTML = `

            <p class="muted">
                Comparing
                ${data.students_found}
                student(s)
            </p>

            <br>

            <table>

                <thead>

                    <tr>

                        <th>Rank</th>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Course</th>
                        <th>Semester</th>
                        <th>Average Marks</th>
                        <th>Attendance</th>

                    </tr>

                </thead>

                <tbody>

                    ${rows}

                </tbody>

            </table>

        `;


    } catch (error) {

        console.error(
            "Comparison error:",
            error
        );


        resultDiv.innerHTML = `
            <p class="muted">
                Unable to compare students.
            </p>
        `;

    }
}


// ============================================================
// TOP STUDENTS
// ============================================================

async function getTopStudents() {

    const resultDiv =
        document.getElementById(
            "analyticsResults"
        );


    resultDiv.innerHTML = `
        <p class="muted">
            Loading top students...
        </p>
    `;


    try {

        const response = await fetch(
            `${API_BASE}/students/top?limit=10`
        );


        if (!response.ok) {
            throw new Error(
                "Failed to load top students"
            );
        }


        const data =
            await response.json();


        resultDiv.innerHTML = `

            <table>

                <thead>

                    <tr>

                        <th>Rank</th>
                        <th>Name</th>
                        <th>Course</th>
                        <th>Semester</th>
                        <th>Average</th>

                    </tr>

                </thead>

                <tbody>

                    ${data.students.map(
                        (student, index) => `

                        <tr>

                            <td>
                                ${index + 1}
                            </td>

                            <td>
                                ${student.name}
                            </td>

                            <td>
                                ${student.course_code}
                            </td>

                            <td>
                                ${student.semester}
                            </td>

                            <td>
                                ${student.average_percentage ?? "-"}%
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        `;


    } catch (error) {

        console.error(
            "Top students error:",
            error
        );


        resultDiv.innerHTML = `
            <p class="muted">
                Unable to load top students.
            </p>
        `;

    }
}


// ============================================================
// HIGH RISK STUDENTS
// ============================================================

async function getHighRiskStudents() {

    const resultDiv =
        document.getElementById(
            "analyticsResults"
        );


    resultDiv.innerHTML = `
        <p class="muted">
            Loading high-risk students...
        </p>
    `;


    try {

        const response = await fetch(
            `${API_BASE}/students/high-risk?limit=10`
        );


        if (!response.ok) {
            throw new Error(
                "Failed to load high-risk students"
            );
        }


        const data =
            await response.json();


        resultDiv.innerHTML = `

            <table>

                <thead>

                    <tr>

                        <th>Rank</th>
                        <th>Name</th>
                        <th>Course</th>
                        <th>Marks</th>
                        <th>Attendance</th>
                        <th>Risk Score</th>
                        <th>Risk Level</th>

                    </tr>

                </thead>

                <tbody>

                    ${data.students.map(
                        (student, index) => `

                        <tr>

                            <td>
                                ${index + 1}
                            </td>

                            <td>
                                ${student.name}
                            </td>

                            <td>
                                ${student.course_code}
                            </td>

                            <td>
                                ${student.average_marks ?? "-"}%
                            </td>

                            <td>
                                ${student.attendance_percentage ?? "-"}%
                            </td>

                            <td>
                                ${student.risk_score ?? "-"}
                            </td>

                            <td>
                                ${getRiskBadge(
                                    student.risk_level
                                )}
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        `;


    } catch (error) {

        console.error(
            "High-risk students error:",
            error
        );


        resultDiv.innerHTML = `
            <p class="muted">
                Unable to load high-risk students.
            </p>
        `;

    }
}


// ============================================================
// LOW ATTENDANCE STUDENTS
// ============================================================

async function getLowAttendanceStudents() {

    const resultDiv =
        document.getElementById(
            "analyticsResults"
        );


    resultDiv.innerHTML = `
        <p class="muted">
            Loading low-attendance students...
        </p>
    `;


    try {

        const response = await fetch(
            `${API_BASE}/students/low-attendance?threshold=75&limit=20`
        );


        if (!response.ok) {
            throw new Error(
                "Failed to load attendance"
            );
        }


        const data =
            await response.json();


        resultDiv.innerHTML = `

            <table>

                <thead>

                    <tr>

                        <th>Rank</th>
                        <th>Name</th>
                        <th>Course</th>
                        <th>Semester</th>
                        <th>Attendance</th>

                    </tr>

                </thead>

                <tbody>

                    ${data.students.map(
                        (student, index) => `

                        <tr>

                            <td>
                                ${index + 1}
                            </td>

                            <td>
                                ${student.name}
                            </td>

                            <td>
                                ${student.course_code}
                            </td>

                            <td>
                                ${student.semester}
                            </td>

                            <td>
                                ${student.attendance_percentage ?? "-"}%
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        `;


    } catch (error) {

        console.error(
            "Low attendance error:",
            error
        );


        resultDiv.innerHTML = `
            <p class="muted">
                Unable to load attendance data.
            </p>
        `;

    }
}


// ============================================================
// DATABASE SUMMARY
// ============================================================

async function getDatabaseSummary() {

    const resultDiv =
        document.getElementById(
            "analyticsResults"
        );


    resultDiv.innerHTML = `
        <p class="muted">
            Loading database summary...
        </p>
    `;


    try {

        const response = await fetch(
            `${API_BASE}/students/database-summary`
        );


        if (!response.ok) {
            throw new Error(
                "Failed to load database summary"
            );
        }


        const data =
            await response.json();


        resultDiv.innerHTML = `

            <div class="student-result">

                <div class="student-info">

                    <div>
                        <strong>Total Students:</strong>
                        ${data.total_students ?? "-"}
                    </div>

                    <div>
                        <strong>Departments:</strong>
                        ${data.total_departments ?? "-"}
                    </div>

                    <div>
                        <strong>Courses:</strong>
                        ${data.total_courses ?? "-"}
                    </div>

                    <div>
                        <strong>Subjects:</strong>
                        ${data.total_subjects ?? "-"}
                    </div>

                    <div>
                        <strong>Mark Records:</strong>
                        ${data.total_mark_records ?? "-"}
                    </div>

                    <div>
                        <strong>Attendance Records:</strong>
                        ${data.total_attendance_records ?? "-"}
                    </div>

                    <div>
                        <strong>Average Marks:</strong>
                        ${data.institution_average ?? "-"}%
                    </div>

                    <div>
                        <strong>Average Attendance:</strong>
                        ${data.institution_attendance ?? "-"}%
                    </div>

                </div>

            </div>

        `;


    } catch (error) {

        console.error(
            "Database summary error:",
            error
        );


        resultDiv.innerHTML = `
            <p class="muted">
                Unable to load database summary.
            </p>
        `;

    }
}


// ============================================================
// ASK AI
// ============================================================

async function askAI() {

    const input =
        document.getElementById("aiQuestion");

    const responseDiv =
        document.getElementById("aiResponse");


    const question =
        input.value.trim();


    if (!question) {

        responseDiv.innerHTML = `
            <p class="muted">
                Please enter a question.
            </p>
        `;

        return;
    }


    responseDiv.innerHTML = `
        <p class="muted">
            🤖 AI is thinking...
        </p>
    `;


    try {

        const response = await fetch(
            `${API_BASE}/ai/chat`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: question
                })
            }
        );


        if (!response.ok) {

            const errorText =
                await response.text();

            console.error(
                "AI API error:",
                errorText
            );

            throw new Error(
                `AI request failed: ${response.status}`
            );
        }


        const data =
            await response.json();


        const answer =
            data.response;


        if (!answer) {

            responseDiv.innerHTML = `
                <p class="muted">
                    AI returned an empty response.
                </p>
            `;

            return;
        }


        // Basic formatting for readable output

        const formattedAnswer =
            String(answer)
                .replace(
                    /\n/g,
                    "<br>"
                );


        responseDiv.innerHTML = `

            <div class="student-result">

                <h3>
                    🤖 Student AI
                </h3>

                <p>
                    ${formattedAnswer}
                </p>

            </div>

        `;


    } catch (error) {

        console.error(
            "AI error:",
            error
        );


        responseDiv.innerHTML = `

            <p class="muted">
                Unable to connect to Student AI.
            </p>

            <p class="muted">
                Please make sure the FastAPI server
                is running.
            </p>

        `;

    }
}


// ============================================================
// AI ENTER KEY SUPPORT
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadDashboard();


        const aiInput =
            document.getElementById(
                "aiQuestion"
            );


        if (aiInput) {

            aiInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                    ) {

                        event.preventDefault();

                        askAI();

                    }

                }
            );

        }

    }
);
