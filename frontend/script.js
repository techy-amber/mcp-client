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
// AI ASSISTANT — VERSION 2.0
// ============================================================

let aiConversationHistory = [];
let currentSpeech = null;


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = String(text ?? "");

    return div.innerHTML;
}


// ============================================================
// BASIC MARKDOWN FORMATTER
// ============================================================

function formatAIResponse(text) {

    let html = escapeHTML(text);

    html = html.replace(
        /```([\s\S]*?)```/g,
        "<pre class=\"ai-code\"><code>$1</code></pre>"
    );

    html = html.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    html = html.replace(
        /^### (.*)$/gm,
        "<h4>$1</h4>"
    );

    html = html.replace(
        /^## (.*)$/gm,
        "<h3>$1</h3>"
    );

    html = html.replace(
        /^# (.*)$/gm,
        "<h2>$1</h2>"
    );

    html = html.replace(
        /^[-*] (.*)$/gm,
        "<li>$1</li>"
    );

    html = html.replace(
        /(<li>.*<\/li>)/gs,
        "<ul>$1</ul>"
    );

    html = html.replace(
        /^\d+\.\s+(.*)$/gm,
        "<li>$1</li>"
    );

    html = html.replace(
        /\n/g,
        "<br>"
    );

    return html;
}


// ============================================================
// RENDER CONVERSATION
// ============================================================

function renderAIConversation() {

    const conversation =
        document.getElementById("aiConversation");

    if (!conversation) {
        return;
    }


    if (aiConversationHistory.length === 0) {

        conversation.innerHTML = `

            <div class="ai-welcome">

                <div class="ai-welcome-icon">
                    🤖
                </div>

                <h3>
                    How can I help you?
                </h3>

                <p class="muted">
                    Ask me about student performance,
                    attendance, marks or risk analysis.
                </p>

                <div class="ai-suggestions">

                    <button
                        type="button"
                        onclick="useAISuggestion('Show me the top 10 students')"
                    >
                        🏆 Top students
                    </button>

                    <button
                        type="button"
                        onclick="useAISuggestion('Show me the high-risk students')"
                    >
                        ⚠️ High-risk students
                    </button>

                    <button
                        type="button"
                        onclick="useAISuggestion('Show me students with attendance below 75%')"
                    >
                        📊 Low attendance
                    </button>

                </div>

            </div>

        `;

        return;
    }


    conversation.innerHTML =
        aiConversationHistory.map(
            (message, index) => {

                if (message.role === "user") {

                    return `

                        <div class="ai-message user-message">

                            <div class="message-label">
                                👤 You
                            </div>

                            <div class="message-bubble user-bubble">
                                ${escapeHTML(message.content)}
                            </div>

                        </div>

                    `;
                }


                return `

                    <div class="ai-message assistant-message">

                        <div class="message-label">
                            🤖 Student AI
                        </div>

                        <div class="message-bubble assistant-bubble">

                            <div class="ai-answer">
                                ${formatAIResponse(message.content)}
                            </div>

                            <div class="ai-message-actions">

                                <button
                                    type="button"
                                    onclick="copyAIResponse(${index})"
                                >
                                    📋 Copy
                                </button>

                                <button
                                    type="button"
                                    onclick="readAIResponse(${index})"
                                >
                                    🔊 Read Aloud
                                </button>

                                <button
                                    type="button"
                                    onclick="shareAIResponse(${index})"
                                >
                                    ↗ Share
                                </button>

                            </div>

                        </div>

                    </div>

                `;

            }
        )
        .join("");


    conversation.scrollTop =
        conversation.scrollHeight;
}


// ============================================================
// ASK AI
// ============================================================

async function askAI() {

    const input =
        document.getElementById("aiQuestion");

    const conversation =
        document.getElementById("aiConversation");

    const sendButton =
        document.getElementById("aiSendButton");


    if (!input || !conversation) {
        return;
    }


    const question =
        input.value.trim();


    if (!question) {
        return;
    }


    aiConversationHistory.push({
        role: "user",
        content: question
    });


    input.value = "";

    input.style.height = "auto";


    renderAIConversation();


    if (sendButton) {
        sendButton.disabled = true;
    }


    const thinking =
        document.createElement("div");

    thinking.className =
        "ai-message assistant-message";

    thinking.innerHTML = `

        <div class="message-label">
            🤖 Student AI
        </div>

        <div class="message-bubble assistant-bubble ai-thinking">

            <span>Thinking</span>

            <span class="thinking-dots">
                <span>.</span>
                <span>.</span>
                <span>.</span>
            </span>

        </div>

    `;

    conversation.appendChild(thinking);

    conversation.scrollTop =
        conversation.scrollHeight;


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

            throw new Error(
                "AI returned an empty response."
            );
        }


        thinking.remove();


        aiConversationHistory.push({
            role: "assistant",
            content: String(answer)
        });


        renderAIConversation();


    } catch (error) {

        console.error(
            "AI error:",
            error
        );


        thinking.remove();


        aiConversationHistory.push({
            role: "assistant",
            content:
                "I was unable to connect to Student AI. Please check the backend connection and try again."
        });


        renderAIConversation();


    } finally {

        if (sendButton) {
            sendButton.disabled = false;
        }

        input.focus();

    }
}


// ============================================================
// SUGGESTION BUTTON
// ============================================================

function useAISuggestion(question) {

    const input =
        document.getElementById("aiQuestion");


    if (!input) {
        return;
    }


    input.value = question;

    input.focus();

    askAI();
}


// ============================================================
// NEW CHAT
// ============================================================

function startNewChat() {

    stopReading();

    aiConversationHistory = [];

    renderAIConversation();


    const input =
        document.getElementById("aiQuestion");


    if (input) {

        input.value = "";

        input.style.height = "auto";

        input.focus();

    }
}


// ============================================================
// COPY AI RESPONSE
// ============================================================

async function copyAIResponse(index) {

    const message =
        aiConversationHistory[index];


    if (
        !message ||
        message.role !== "assistant"
    ) {
        return;
    }


    try {

        await navigator.clipboard.writeText(
            message.content
        );

        showTemporaryMessage("Copied!");


    } catch (error) {

        console.error(
            "Copy failed:",
            error
        );

    }
}


// ============================================================
// TEMPORARY NOTIFICATION
// ============================================================

function showTemporaryMessage(message) {

    const notification =
        document.createElement("div");

    notification.className =
        "ai-toast";

    notification.textContent =
        message;


    document.body.appendChild(
        notification
    );


    setTimeout(
        () => {
            notification.remove();
        },
        1800
    );
}


// ============================================================
// READ ALOUD
// ============================================================

function readAIResponse(index) {

    const message =
        aiConversationHistory[index];


    if (
        !message ||
        message.role !== "assistant"
    ) {
        return;
    }


    if (
        !("speechSynthesis" in window)
    ) {

        showTemporaryMessage(
            "Read Aloud is not supported by this browser."
        );

        return;
    }


    stopReading();


    currentSpeech =
        new SpeechSynthesisUtterance(
            message.content
        );


    currentSpeech.rate = 1;
    currentSpeech.pitch = 1;
    currentSpeech.volume = 1;


    currentSpeech.onend = function () {

        currentSpeech = null;

    };


    currentSpeech.onerror =
        function () {

            currentSpeech = null;

        };


    window.speechSynthesis.speak(
        currentSpeech
    );

}


// ============================================================
// STOP READING
// ============================================================

function stopReading() {

    if (
        "speechSynthesis" in window
    ) {

        window.speechSynthesis.cancel();

    }


    currentSpeech = null;
}


// ============================================================
// SHARE AI RESPONSE
// ============================================================

async function shareAIResponse(index) {

    const message =
        aiConversationHistory[index];


    if (
        !message ||
        message.role !== "assistant"
    ) {
        return;
    }


    const shareData = {

        title:
            "Student AI Response",

        text:
            message.content

    };


    try {

        if (navigator.share) {

            await navigator.share(
                shareData
            );

        } else {

            await navigator.clipboard.writeText(
                message.content
            );


            showTemporaryMessage(
                "Response copied — ready to share!"
            );

        }

    } catch (error) {

        if (
            error.name !== "AbortError"
        ) {

            console.error(
                "Share failed:",
                error
            );

        }

    }
}


// ============================================================
// AI KEYBOARD SUPPORT
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadDashboard();


        const aiInput =
            document.getElementById(
                "aiQuestion"
            );


        if (!aiInput) {
            return;
        }


        aiInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    askAI();

                }

            }
        );


        aiInput.addEventListener(
            "input",
            function () {

                this.style.height =
                    "auto";

                this.style.height =
                    Math.min(
                        this.scrollHeight,
                        160
                    ) + "px";

            }
        );

    }
);