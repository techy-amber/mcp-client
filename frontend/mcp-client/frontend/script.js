const API_BASE = "https://mcp-client-ncph.onrender.com";


// ============================================================
// Database Summary
// ============================================================

async function loadDashboard() {
    try {
        const response = await fetch(
            `${API_BASE}/students/database-summary`
        );

        if (!response.ok) {
            throw new Error("Failed to load database summary");
        }

        const data = await response.json();

        document.getElementById("totalStudents").textContent =
            data.total_students;

        document.getElementById("totalCourses").textContent =
            data.total_courses;

        document.getElementById("averageMarks").textContent =
            `${data.institution_average}%`;

        document.getElementById("averageAttendance").textContent =
            `${data.institution_attendance}%`;

    } catch (error) {
        console.error(error);

        document.getElementById("totalStudents").textContent = "Error";
        document.getElementById("totalCourses").textContent = "Error";
        document.getElementById("averageMarks").textContent = "Error";
        document.getElementById("averageAttendance").textContent = "Error";
    }
}


// ============================================================
// Search Students
// ============================================================

async function searchStudent() {

    const searchTerm =
        document.getElementById("searchInput").value.trim();

    const resultDiv =
        document.getElementById("searchResults");

    if (!searchTerm) {
        resultDiv.innerHTML =
            `<p class="muted">Please enter a student name or enrollment number.</p>`;
        return;
    }

    resultDiv.innerHTML =
        `<p class="muted">Searching...</p>`;

    try {

        const response = await fetch(
            `${API_BASE}/students/search?search_term=${encodeURIComponent(searchTerm)}`
        );

        if (!response.ok) {
            throw new Error("Search failed");
        }

        const data = await response.json();

        if (data.count === 0) {
            resultDiv.innerHTML =
                `<p class="muted">No students found.</p>`;
            return;
        }

        resultDiv.innerHTML = data.students.map(student => `

            <div class="student-result">

                <h3>${student.name}</h3>

                <div class="student-info">

                    <div>
                        <strong>ID:</strong>
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

                </div>

            </div>

        `).join("");

    } catch (error) {

        console.error(error);

        resultDiv.innerHTML =
            `<p class="muted">Unable to connect to the backend.</p>`;
    }
}


// ============================================================
// Top Students
// ============================================================

async function getTopStudents() {

    const resultDiv =
        document.getElementById("analyticsResults");

    resultDiv.innerHTML =
        `<p class="muted">Loading top students...</p>`;

    try {

        const response = await fetch(
            `${API_BASE}/students/top?limit=10`
        );

        if (!response.ok) {
            throw new Error("Failed to load top students");
        }

        const data = await response.json();

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

                    ${data.students.map((student, index) => `

                        <tr>

                            <td>${index + 1}</td>

                            <td>${student.name}</td>

                            <td>${student.course_code}</td>

                            <td>${student.semester}</td>

                            <td>
                                ${student.average_percentage}%
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        `;

    } catch (error) {

        console.error(error);

        resultDiv.innerHTML =
            `<p class="muted">Unable to load top students.</p>`;
    }
}


// ============================================================
// High Risk Students
// ============================================================

async function getHighRiskStudents() {

    const resultDiv =
        document.getElementById("analyticsResults");

    resultDiv.innerHTML =
        `<p class="muted">Loading high-risk students...</p>`;

    try {

        const response = await fetch(
            `${API_BASE}/students/high-risk?limit=10`
        );

        if (!response.ok) {
            throw new Error("Failed to load high-risk students");
        }

        const data = await response.json();

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

                    ${data.students.map((student, index) => `

                        <tr>

                            <td>${index + 1}</td>

                            <td>${student.name}</td>

                            <td>${student.course_code}</td>

                            <td>${student.average_marks}%</td>

                            <td>${student.attendance_percentage}%</td>

                            <td>${student.risk_score}</td>

                            <td>${student.risk_level}</td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        `;

    } catch (error) {

        console.error(error);

        resultDiv.innerHTML =
            `<p class="muted">Unable to load high-risk students.</p>`;
    }
}


// ============================================================
// Low Attendance Students
// ============================================================

async function getLowAttendanceStudents() {

    const resultDiv =
        document.getElementById("analyticsResults");

    resultDiv.innerHTML =
        `<p class="muted">Loading low-attendance students...</p>`;

    try {

        const response = await fetch(
            `${API_BASE}/students/low-attendance?threshold=75&limit=20`
        );

        if (!response.ok) {
            throw new Error("Failed to load attendance data");
        }

        const data = await response.json();

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

                    ${data.students.map((student, index) => `

                        <tr>

                            <td>${index + 1}</td>

                            <td>${student.name}</td>

                            <td>${student.course_code}</td>

                            <td>${student.semester}</td>

                            <td>
                                ${student.attendance_percentage}%
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        `;

    } catch (error) {

        console.error(error);

        resultDiv.innerHTML =
            `<p class="muted">Unable to load attendance data.</p>`;
    }
}


// ============================================================
// Database Summary
// ============================================================

async function getDatabaseSummary() {

    const resultDiv =
        document.getElementById("analyticsResults");

    resultDiv.innerHTML =
        `<p class="muted">Loading database summary...</p>`;

    try {

        const response = await fetch(
            `${API_BASE}/students/database-summary`
        );

        if (!response.ok) {
            throw new Error("Failed to load database summary");
        }

        const data = await response.json();

        resultDiv.innerHTML = `

            <div class="student-result">

                <div class="student-info">

                    <div>
                        <strong>Total Students:</strong>
                        ${data.total_students}
                    </div>

                    <div>
                        <strong>Departments:</strong>
                        ${data.total_departments}
                    </div>

                    <div>
                        <strong>Courses:</strong>
                        ${data.total_courses}
                    </div>

                    <div>
                        <strong>Subjects:</strong>
                        ${data.total_subjects}
                    </div>

                    <div>
                        <strong>Mark Records:</strong>
                        ${data.total_mark_records}
                    </div>

                    <div>
                        <strong>Attendance Records:</strong>
                        ${data.total_attendance_records}
                    </div>

                    <div>
                        <strong>Average Marks:</strong>
                        ${data.institution_average}%
                    </div>

                    <div>
                        <strong>Average Attendance:</strong>
                        ${data.institution_attendance}%
                    </div>

                </div>

            </div>

        `;

    } catch (error) {

        console.error(error);

        resultDiv.innerHTML =
            `<p class="muted">Unable to load database summary.</p>`;
    }
}


// ============================================================
// Load dashboard when page opens
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});