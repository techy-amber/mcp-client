\# Student AI Analytics



Student AI Analytics is a web-based student management and analytics project.



The project combines:



\- A simple web dashboard

\- FastAPI backend

\- Student business logic

\- Database operations

\- MCP (Model Context Protocol) tools

\- Qwen AI through Groq

\- Natural-language AI chatbot



The main idea is simple:



A user can either use the normal dashboard or ask the AI a question in normal English.



The AI can use controlled MCP tools to get real student information and then explain the result in simple language.





\# 1. Project Objective



The objective of this project is to make student information easier to search, analyze and understand.



Instead of manually checking different records, a user can:



\- Search for a student

\- View marks

\- View attendance

\- Calculate average marks

\- Compare students

\- Find top students

\- Find low-attendance students

\- Find high-risk students

\- Analyze course and semester performance

\- Ask questions using the AI chatbot



For example, instead of finding an API and entering parameters manually, the user can ask:



"What is the average of student 100776?"



or:



"Which students have low attendance?"



or:



"Compare students 100001, 100002 and 100003."





\# 2. Main Features



\## Student Management



\- Search students

\- View complete student information

\- View marks

\- View attendance

\- Calculate average marks

\- Find weakest subject



\## Analytics



\- Top students

\- High-risk students

\- Low-attendance students

\- At-risk students

\- Course performance

\- Semester performance

\- Class statistics

\- Weak subjects

\- Subject performance

\- Database summary



\## Student Comparison



The system can compare multiple students using:



\- Average marks

\- Attendance

\- Course

\- Semester

\- Student information



\## AI Assistant



The AI chatbot allows users to ask questions in normal language.



Examples:



"What is the average of student 100776?"



"Which students have attendance below 75%?"



"Compare students 100001, 100002 and 100003."



The AI uses MCP tools when real student data is required.


**# 3. Technologies Used**



**| Technology | Purpose |**

**|---|---|**

**| HTML | Frontend structure |**

**| CSS | Frontend design |**

**| JavaScript | Frontend logic and API calls |**

**| Python | Backend and AI logic |**

**| FastAPI | REST API backend |**

**| MySQL / Student Database | Store student information |**

**| StudentService | Student business logic |**

**| MCP | Connect AI with external tools |**

**| Qwen | AI language model |**

**| Groq | Model API |**

**| Python MCP SDK | MCP client/server communication |**





**# 4. High-Level Architecture**



**The project has two main paths.**



**## Normal Dashboard Path**



**When the user uses a normal dashboard feature:**



**User**

&#x20; **|**

&#x20; **v**

**Frontend**

&#x20; **|**

&#x20; **v**

**FastAPI API**

&#x20; **|**

&#x20; **v**

**StudentService**

&#x20; **|**

&#x20; **v**

**Database**

&#x20; **|**

&#x20; **v**

**StudentService**

&#x20; **|**

&#x20; **v**

**FastAPI**

&#x20; **|**

&#x20; **v**

**Frontend**





**## AI Path**



**When the user asks a natural-language question:**



**User**

&#x20; **|**

&#x20; **v**

**Frontend AI Chatbot**

&#x20; **|**

&#x20; **v**

**FastAPI /ai/chat**

&#x20; **|**

&#x20; **v**

**Student AI Assistant**

&#x20; **|**

&#x20; **v**

**Qwen through Groq**

&#x20; **|**

&#x20; **v**

**Select MCP Tool**

&#x20; **|**

&#x20; **v**

**Student MCP Server**

&#x20; **|**

&#x20; **v**

**StudentService**

&#x20; **|**

&#x20; **v**

**Database**

&#x20; **|**

&#x20; **v**

**MCP Tool Result**

&#x20; **|**

&#x20; **v**

**Qwen**

&#x20; **|**

&#x20; **v**

**Natural Language Response**

&#x20; **|**

&#x20; **v**

**Frontend**





**# 5. Detailed Project Flow**



**The complete system works in the following order:**



&#x20;                   **+----------------------+**

&#x20;                   **|        USER          |**

&#x20;                   **+----------+-----------+**

&#x20;                              **|**

&#x20;                              **v**

&#x20;                   **+----------------------+**

&#x20;                   **|      FRONTEND        |**

&#x20;                   **| HTML + CSS + JS      |**

&#x20;                   **+----------+-----------+**

&#x20;                              **|**

&#x20;                **+-------------+-------------+**

&#x20;                **|                           |**

&#x20;                **v                           v**

&#x20;      **+------------------+        +------------------+**

&#x20;      **| Normal Dashboard |        |   AI Chatbot     |**

&#x20;      **+--------+---------+        +--------+---------+**

&#x20;               **|                           |**

&#x20;               **v                           v**

&#x20;      **+------------------+        +------------------+**

&#x20;      **|    FastAPI       |        |  /ai/chat API    |**

&#x20;      **+--------+---------+        +--------+---------+**

&#x20;               **|                           |**

&#x20;               **v                           v**

&#x20;      **+------------------+        +------------------+**

&#x20;      **| StudentService   |        | Student AI       |**

&#x20;      **| Business Logic   |        | Assistant        |**

&#x20;      **+--------+---------+        +--------+---------+**

&#x20;               **|                           |**

&#x20;               **v                           v**

&#x20;      **+------------------+        +------------------+**

&#x20;      **|     Database     |        | Qwen / Groq      |**

&#x20;      **+--------+---------+        +--------+---------+**

&#x20;               **|                           |**

&#x20;               **|                           v**

&#x20;               **|                  +------------------+**

&#x20;               **|                  |   MCP Tool       |**

&#x20;               **|                  |   Selection      |**

&#x20;               **|                  +--------+---------+**

&#x20;               **|                           |**

&#x20;               **|                           v**

&#x20;               **|                  +------------------+**

&#x20;               **|                  | Student MCP      |**

&#x20;               **|                  | Server           |**

&#x20;               **|                  +--------+---------+**

&#x20;               **|                           |**

&#x20;               **+---------------------------+**

&#x20;                           **|**

&#x20;                           **v**

&#x20;                   **+------------------+**

&#x20;                   **| Actual Student   |**

&#x20;                   **| Data             |**

&#x20;                   **+--------+---------+**

&#x20;                            **|**

&#x20;                            **v**

&#x20;                   **+------------------+**

&#x20;                   **| AI Natural       |**

&#x20;                   **| Language Answer   |**

&#x20;                   **+--------+---------+**

&#x20;                            **|**

&#x20;                            **v**

&#x20;                   **+------------------+**

&#x20;                   **| Frontend Chat    |**

&#x20;                   **+------------------+**





**# 6. Folder Structure**



**The important project structure is:**



**mcp-client/**

**|**

**├── README.md**

**|**

**├── frontend/**

**│   ├── index.html**

**│   ├── script.js**

**│   └── style.css**

**|**

**├── src/**

**│   |**

**│   ├── api/**

**│   │   ├── \_\_init\_\_.py**

**│   │   ├── ai\_routes.py**

**│   │   ├── app.py**

**│   │   ├── calculator\_routes.py**

**│   │   └── student\_routes.py**

**│   |**

**│   └── services/**

**│       └── calculator\_service.py**

**|**

**├── MCP servers/**

**│   ├── Student MCP Server**

**│   └── Calculator MCP Server**

**|**

**├── AI Service**

**│   └── StudentAIAssistant**

**│**

**└── .env**





**The exact location or name of some MCP and AI service files can depend on the local project structure.**



**The important separation is:**



**Frontend**

**API Layer**

**Service Layer**

**MCP Layer**

**AI Layer**

**Database**

# 7. Frontend



\## index.html



This file creates the main dashboard structure.



It contains sections such as:



\- Dashboard statistics

\- Student search

\- Search results

\- Analytics

\- Analytics results

\- Student comparison

\- AI chatbot



The HTML defines what the user sees on the webpage.





\## style.css



This file controls the appearance of the dashboard.



It handles:



\- Cards

\- Buttons

\- Tables

\- Grid layout

\- Spacing

\- Responsive design

\- Mobile layout





\## script.js



This file contains the frontend functionality.



It communicates with FastAPI using JavaScript fetch() requests.



Important functions include:



loadDashboard()

searchStudent()

viewStudentDetails()

compareStudents()

getTopStudents()

getHighRiskStudents()

getLowAttendanceStudents()

getDatabaseSummary()

askAI()



Basic frontend flow:



User Action

&#x20;   |

&#x20;   v

JavaScript Function

&#x20;   |

&#x20;   v

fetch() Request

&#x20;   |

&#x20;   v

FastAPI Endpoint

&#x20;   |

&#x20;   v

JSON Response

&#x20;   |

&#x20;   v

JavaScript

&#x20;   |

&#x20;   v

Update Webpage





\# 8. Backend



FastAPI is used as the main backend framework.



The backend is responsible for:



1\. Receiving requests from the frontend

2\. Calling the required service

3\. Returning JSON responses

4\. Providing the AI chat endpoint

5\. Handling CORS



The main FastAPI application is:



src/api/app.py





\# 9. API Layer



The API layer is responsible for handling HTTP requests.



\## Student Routes



student\_routes.py contains endpoints for student operations.



Examples:



GET /students/search



GET /students/compare



GET /students/top



GET /students/at-risk



GET /students/high-risk



GET /students/low-attendance



GET /students/database-summary



GET /students/course-performance



GET /students/semester-performance



GET /students/class-statistics



GET /students/weak-subjects



GET /students/subject-performance





Individual student operations include:



GET /students/{student\_id}



GET /students/{student\_id}/marks



GET /students/{student\_id}/attendance



GET /students/{student\_id}/average



GET /students/{student\_id}/weakest-subject



GET /students/{student\_id}/risk





The route layer does not contain all the business logic.



Instead, it calls StudentService.



Example:



HTTP Request

&#x20;    |

&#x20;    v

Student Route

&#x20;    |

&#x20;    v

StudentService

&#x20;    |

&#x20;    v

Database





\# 10. StudentService



StudentService is the business logic layer for student operations.



It handles operations such as:



\- Search student

\- Get student details

\- Get marks

\- Get attendance

\- Calculate average

\- Compare students

\- Find top students

\- Find high-risk students

\- Find low-attendance students

\- Course performance

\- Semester performance

\- Weak subjects

\- Subject performance

\- Database summary



This separation makes the project easier to maintain.



For example:



Route

&#x20; |

&#x20; | "I received a request for student 100776"

&#x20; v

StudentService

&#x20; |

&#x20; | "Find the student's attendance"

&#x20; v

Database

&#x20; |

&#x20; | "Return attendance records"

&#x20; v

StudentService

&#x20; |

&#x20; | "Prepare the result"

&#x20; v

Route

&#x20; |

&#x20; | "Return JSON response"

&#x20; v

Frontend





\# 11. MCP Architecture



MCP stands for:



Model Context Protocol



In this project, MCP is used as the bridge between the AI model and external capabilities.



There are two important tool groups:



\- Student MCP Tools

\- Calculator MCP Tools



The AI does not directly write SQL or directly access the database.



Instead:



AI

&#x20;|

&#x20;v

MCP Tool

&#x20;|

&#x20;v

Application Service

&#x20;|

&#x20;v

Database



This gives the AI controlled access to the required operations.





\# 12. How MCP Tools Are Discovered



When the AI service starts:



Start AI Assistant

&#x20;      |

&#x20;      v

Connect to Calculator MCP

&#x20;      |

&#x20;      v

Connect to Student MCP

&#x20;      |

&#x20;      v

Discover available tools

&#x20;      |

&#x20;      v

Convert tools to model-compatible definitions

&#x20;      |

&#x20;      v

Give tools to Qwen





The AI service uses MCP clients to discover the available tools.



The discovered tools are then converted into tool definitions that the AI model can understand.





\# 13. AI Assistant Flow



The main AI component is:



StudentAIAssistant



Its main responsibilities are:



1\. Start MCP connections

2\. Discover tools

3\. Maintain conversation

4\. Send user request to Qwen

5\. Let Qwen decide whether a tool is required

6\. Execute selected MCP tool

7\. Send tool result back to Qwen

8\. Generate final answer



Detailed flow:



&#x20;             USER QUESTION

&#x20;                   |

&#x20;                   v

&#x20;       +------------------------+

&#x20;       | StudentAIAssistant     |

&#x20;       +-----------+------------+

&#x20;                   |

&#x20;                   v

&#x20;       +------------------------+

&#x20;       | Qwen Model through     |

&#x20;       | Groq                   |

&#x20;       +-----------+------------+

&#x20;                   |

&#x20;                   v

&#x20;       +------------------------+

&#x20;       | Is a tool required?    |

&#x20;       +-----+-------------+----+

&#x20;             |             |

&#x20;            NO            YES

&#x20;             |             |

&#x20;             |             v

&#x20;             |     +---------------+

&#x20;             |     | Select MCP    |

&#x20;             |     | Tool           |

&#x20;             |     +-------+-------+

&#x20;             |             |

&#x20;             |             v

&#x20;             |     +---------------+

&#x20;             |     | Execute MCP   |

&#x20;             |     | Tool           |

&#x20;             |     +-------+-------+

&#x20;             |             |

&#x20;             |             v

&#x20;             |     +---------------+

&#x20;             |     | Get actual    |

&#x20;             |     | data/result   |

&#x20;             |     +-------+-------+

&#x20;             |             |

&#x20;             +-------------+

&#x20;                           |

&#x20;                           v

&#x20;                 +-------------------+

&#x20;                 | Qwen generates    |

&#x20;                 | final response    |

&#x20;                 +---------+---------+

&#x20;                           |

&#x20;                           v

&#x20;                        USER





\# 14. Example: Average Marks



Suppose the user asks:



What is the average of student 100776?



The detailed flow is:



1\. User enters the question

&#x20;         |

&#x20;         v

2\. Frontend sends request

&#x20;         |

&#x20;         v

3\. FastAPI receives /ai/chat

&#x20;         |

&#x20;         v

4\. StudentAIAssistant receives question

&#x20;         |

&#x20;         v

5\. Qwen receives available MCP tools

&#x20;         |

&#x20;         v

6\. Qwen identifies that student data is required

&#x20;         |

&#x20;         v

7\. Qwen selects the appropriate student tool

&#x20;         |

&#x20;         v

8\. MCP executes the tool

&#x20;         |

&#x20;         v

9\. StudentService retrieves student data

&#x20;         |

&#x20;         v

10\. Database returns the required information

&#x20;         |

&#x20;         v

11\. MCP returns the result

&#x20;         |

&#x20;         v

12\. Result is given back to Qwen

&#x20;         |

&#x20;         v

13\. Qwen creates a simple answer

&#x20;         |

&#x20;         v

14\. Frontend displays the answer



Example final response:



The average marks for student 100776

(Aryan Agarwal) are 51.78.

# 15. Example: Low Attendance



User:



Which students have attendance below 75%?



Flow:



User

&#x20;|

&#x20;v

AI

&#x20;|

&#x20;v

Low Attendance MCP Tool

&#x20;|

&#x20;v

StudentService

&#x20;|

&#x20;v

Database

&#x20;|

&#x20;v

Students below 75%

&#x20;|

&#x20;v

MCP Result

&#x20;|

&#x20;v

AI

&#x20;|

&#x20;v

Readable Table

&#x20;|

&#x20;v

User



The system can return:



\- Student ID

\- Student name

\- Course

\- Semester

\- Section

\- Attendance percentage



Example:



The system can identify students whose attendance is below

the configured threshold.





\# 16. Example: Student Comparison



User:



Compare students 100001, 100002 and 100003.



Flow:



User

&#x20;|

&#x20;v

AI

&#x20;|

&#x20;v

Comparison MCP Tool

&#x20;|

&#x20;v

StudentService

&#x20;|

&#x20;v

Database

&#x20;|

&#x20;v

Three student records

&#x20;|

&#x20;v

MCP Result

&#x20;|

&#x20;v

AI

&#x20;|

&#x20;v

Comparison Table + Summary

&#x20;|

&#x20;v

User



Example result:



Harsh Shah

Average Marks: 84.87

Attendance: 85.42%



Aryan Verma

Average Marks: 69.32

Attendance: 80.41%



Kavya Yadav

Average Marks: 69.31

Attendance: 75.66%





\# 17. Normal API Flow vs AI Flow



\## Normal API



User clicks button

&#x20;     |

&#x20;     v

JavaScript fetch()

&#x20;     |

&#x20;     v

FastAPI

&#x20;     |

&#x20;     v

Student Route

&#x20;     |

&#x20;     v

StudentService

&#x20;     |

&#x20;     v

Database

&#x20;     |

&#x20;     v

JSON Response

&#x20;     |

&#x20;     v

Frontend





\## AI Query



User asks question

&#x20;     |

&#x20;     v

JavaScript fetch()

&#x20;     |

&#x20;     v

FastAPI /ai/chat

&#x20;     |

&#x20;     v

StudentAIAssistant

&#x20;     |

&#x20;     v

Qwen / Groq

&#x20;     |

&#x20;     v

MCP Tool Selection

&#x20;     |

&#x20;     v

MCP Server

&#x20;     |

&#x20;     v

StudentService

&#x20;     |

&#x20;     v

Database

&#x20;     |

&#x20;     v

MCP Result

&#x20;     |

&#x20;     v

Qwen

&#x20;     |

&#x20;     v

Natural Language Response

&#x20;     |

&#x20;     v

Frontend





\# 18. Why Use AI?



Traditional dashboard:



The user normally needs to:



\- Know which feature to open

\- Search for a student

\- Select the required analytics option

\- Apply the required filter



With AI, the user can simply ask:



"Which students have low attendance?"



or:



"Compare these three students."



The AI understands the natural-language question and selects

the required tool.



Therefore, AI provides a natural-language interface over the

existing student analytics system.





\# 19. Why Use MCP?



MCP provides a controlled bridge between the AI and external tools.



Without this separation:



AI

&#x20;|

&#x20;v

Direct Database Access



With MCP:



AI

&#x20;|

&#x20;v

MCP Tool

&#x20;|

&#x20;v

Service Layer

&#x20;|

&#x20;v

Database



Advantages:



\- Controlled access

\- Better separation of responsibilities

\- Reusable tools

\- Easier to add new tools

\- AI does not need to know database implementation details

\- Database logic stays inside the application layer





\# 20. CORS



During local development, the frontend and backend run on

different ports.



Frontend:



http://127.0.0.1:5500



Backend:



http://127.0.0.1:8000



Because these are different origins, the backend uses FastAPI's

CORS middleware to allow the frontend to communicate with it.



Basic flow:



Frontend

&#x20;  |

&#x20;  | HTTP Request

&#x20;  v

FastAPI

&#x20;  |

&#x20;  | CORS allows request

&#x20;  v

Backend Response

&#x20;  |

&#x20;  v

Frontend





\# 21. Running the Project



\## Step 1: Start Backend



Open Command Prompt and run:



cd C:\\Users\\hp\\mcp-client



Then:



uv run uvicorn api.app:app --app-dir src



Backend address:



http://127.0.0.1:8000





\## Step 2: Open API Documentation



Open:



http://127.0.0.1:8000/docs



This opens FastAPI Swagger documentation.



Swagger can be used to test the backend APIs directly.





\## Step 3: Start Frontend



Open another Command Prompt.



Run:



cd C:\\Users\\hp\\mcp-client



Then:



uv run python -m http.server 5500 --directory frontend



Frontend address:



http://127.0.0.1:5500





Keep both backend and frontend terminals running.





\# 22. Environment Variables



The AI service uses the Groq API key through an environment

file.



Example:



GROQ\_API\_KEY=your\_groq\_api\_key



Do not put the real API key inside frontend JavaScript.



Do not publish the real API key to GitHub.



A .gitignore file should normally contain:



.env

\_\_pycache\_\_/

\*.pyc





\# 23. Testing



Important tests used during development include:





\## Test 1: Student Average



Question:



What is the average of student 100776?



Expected result:



51.78





\## Test 2: Low Attendance



Question:



Which students have low attendance?



Expected result:



The system returns students below the configured attendance

threshold.



The result can contain:



\- Student ID

\- Name

\- Course

\- Semester

\- Section

\- Attendance percentage





\## Test 3: High Risk



Question:



Which students are at high risk?



Expected result:



\- Student ID

\- Name

\- Course

\- Semester

\- Average marks

\- Attendance

\- Risk score





\## Test 4: Student Comparison



Question:



Compare students 100001, 100002 and 100003.



Expected result:



100002

Average Marks: 84.87

Attendance: 85.42%



100001

Average Marks: 69.32

Attendance: 80.41%



100003

Average Marks: 69.31

Attendance: 75.66%





\# 24. End-to-End Test Flow



The final end-to-end test should look like this:



Start Backend

&#x20;     |

&#x20;     v

Start Frontend

&#x20;     |

&#x20;     v

Open Dashboard

&#x20;     |

&#x20;     v

Check Dashboard Statistics

&#x20;     |

&#x20;     v

Search Student 100776

&#x20;     |

&#x20;     v

View Student Details

&#x20;     |

&#x20;     v

Check Marks and Attendance

&#x20;     |

&#x20;     v

Open High Risk Students

&#x20;     |

&#x20;     v

Open Low Attendance Students

&#x20;     |

&#x20;     v

Compare Students

100001, 100002, 100003

&#x20;     |

&#x20;     v

Open AI Chatbot

&#x20;     |

&#x20;     v

Ask Student Question

&#x20;     |

&#x20;     v

AI Selects MCP Tool

&#x20;     |

&#x20;     v

MCP Gets Real Data

&#x20;     |

&#x20;     v

AI Generates Response

&#x20;     |

&#x20;     v

Response Appears on Dashboard

25. Error Handling



The system handles common problems such as:



Empty search

Student not found

Backend unavailable

AI service error

Invalid tool request

Large conversation context

Temporary AI rate limits



During development, the AI service can temporarily return

a 429 rate-limit error from the Groq API.



A 429 error means the model API has temporarily reached its

usage limit. It does not automatically mean that the database,

MCP server or student APIs are broken.



The system can be retried after the rate-limit window passes.



26\. Security Considerations



Basic security practices for this project include:



Never expose the Groq API key in frontend JavaScript

Keep API keys in .env

Do not give the AI direct database credentials

Use controlled MCP tools

Validate tool arguments

Keep database logic inside the service layer

Do not expose internal database implementation to users

27\. Advantages

1\. Easy to Use



Users can use either the dashboard or natural-language AI.



2\. Real Student Data



AI answers can be based on student information retrieved

through the available tools.



3\. Modular Architecture



Frontend, API, service, MCP and AI layers are separated.



4\. Extensible



New MCP tools can be added later.



Possible future tools include:



Attendance Prediction Tool

Performance Prediction Tool

Report Generation Tool

Course Recommendation Tool

5\. Useful Analytics



The system can quickly identify students who may require

academic attention.



28\. Limitations



Current limitations include:



AI responses depend on model/API availability

Groq rate limits can temporarily affect AI responses

The project currently uses a local development setup

Natural-language response quality depends on the AI model

AI should not be treated as the final authority for academic

decisions

Production use would require proper authentication and

authorization

29\. Future Improvements



Possible future features include:



Student performance prediction

Attendance prediction

Personalized recommendations

Teacher dashboard

Parent dashboard

Authentication

Role-based access

Charts and graphs

PDF report generation

Notifications for high-risk students

More MCP tools

Cloud deployment

30\. Future System

&#x20;                    Future System

&#x20;                         |

&#x20;     +-------------------+-------------------+

&#x20;     |                   |                   |

&#x20;     v                   v                   v



Performance Attendance Recommendation

Prediction Prediction System

| | |

+-------------------+-------------------+

|

v

Advanced AI

Assistant



31\. Complete Project Flowchart

&#x20;                    +----------------+

&#x20;                    |      USER      |

&#x20;                    +-------+--------+

&#x20;                            |

&#x20;                            v

&#x20;               +------------------------+

&#x20;               |      WEB DASHBOARD     |

&#x20;               |     HTML/CSS/JS        |

&#x20;               +-----------+------------+

&#x20;                           |

&#x20;              +------------+------------+

&#x20;              |                         |

&#x20;              v                         v

&#x20;     +----------------+        +----------------+

&#x20;     | Normal APIs   |        |   AI Chatbot   |

&#x20;     +-------+--------+        +-------+--------+

&#x20;             |                         |

&#x20;             v                         v

&#x20;     +----------------+        +----------------+

&#x20;     |    FastAPI     |        | AI Chat API    |

&#x20;     +-------+--------+        +-------+--------+

&#x20;             |                         |

&#x20;             v                         v

&#x20;     +----------------+        +----------------+

&#x20;     | Student Routes |        | Student AI     |

&#x20;     +-------+--------+        | Assistant      |

&#x20;             |                 +-------+--------+

&#x20;             v                         |

&#x20;     +----------------+                v

&#x20;     | StudentService |        +----------------+

&#x20;     +-------+--------+        | Qwen / Groq    |

&#x20;             |                 +-------+--------+

&#x20;             v                         |

&#x20;     +----------------+                v

&#x20;     |    Database    |        +----------------+

&#x20;     +-------+--------+        | MCP Tool       |

&#x20;             |                 | Selection      |

&#x20;             |                 +-------+--------+

&#x20;             |                         |

&#x20;             |                         v

&#x20;             |                 +----------------+

&#x20;             +---------------->| MCP Server     |

&#x20;                               +-------+--------+

&#x20;                                       |

&#x20;                                       v

&#x20;                               +----------------+

&#x20;                               | StudentService |

&#x20;                               +-------+--------+

&#x20;                                       |

&#x20;                                       v

&#x20;                               +----------------+

&#x20;                               |    Database    |

&#x20;                               +-------+--------+

&#x20;                                       |

&#x20;                                       v

&#x20;                               +----------------+

&#x20;                               | MCP Tool Result|

&#x20;                               +-------+--------+

&#x20;                                       |

&#x20;                                       v

&#x20;                               +----------------+

&#x20;                               | Qwen / Groq    |

&#x20;                               +-------+--------+

&#x20;                                       |

&#x20;                                       v

&#x20;                               +----------------+

&#x20;                               | AI Response    |

&#x20;                               +-------+--------+

&#x20;                                       |

&#x20;                                       v

&#x20;                               +----------------+

&#x20;                               |      USER      |

&#x20;                               +----------------+

32\. Project Summary



Student AI Analytics combines a normal student management

dashboard with an AI-powered natural-language interface.



The normal dashboard handles direct operations such as:



Searching students

Viewing marks

Checking attendance

Running analytics

Comparing students



The AI assistant adds another way to interact with the same

system.



It uses Qwen through Groq and MCP tools to understand user

questions, retrieve the required student information and

generate a readable response.



The main architecture is:



Frontend

|

v

FastAPI

|

v

Services

|

v

Database



AI

|

v

MCP Tools

|

v

Services

|

v

Database



33\. One-Line Project Explanation



Student AI Analytics is a full-stack student management and

analytics system where FastAPI provides the backend,

StudentService handles business logic and database operations,

and an AI assistant uses MCP tools to answer student-related

questions using natural language.



34\. Important Demo Questions



During a project demonstration, the following questions can

be asked:



Why did you use FastAPI?

What is MCP?

Why did you use MCP?

Why not give direct database access to AI?

What is the role of StudentService?

How does AI select the appropriate tool?

How does the frontend communicate with the backend?

What is CORS?

How are high-risk students identified?

Explain the complete flow of one AI query.

35\. Recommended Demo Sequence



For a short project demonstration, use this order:



Open the dashboard

Show dashboard statistics

Search student 100776

Show student details

Show marks and attendance

Open High Risk Students

Open Low Attendance Students

Compare students 100001, 100002 and 100003

Open AI chatbot

Ask:



"What is the average of student 100776?"



Ask:



"Which students have low attendance?"



Ask:



"Compare students 100001, 100002 and 100003."



Explain the AI -> MCP -> Service -> Database flow.

36\. Final Architecture in Simple Words



The easiest way to understand the project is:



The frontend is what the user sees.



FastAPI receives requests from the frontend.



The API layer decides which backend operation is required.



StudentService contains the actual student-related business logic.



The database stores the student information.



The AI assistant understands natural-language questions.



MCP provides controlled tools that the AI can use.



The AI selects the appropriate tool, the tool gets the real data,

and the AI converts the result into a simple response for the user.



So the complete system is:



USER

|

v

FRONTEND

|

v

FASTAPI

|

+----------------------+

| |

v v

STUDENT APIs AI ASSISTANT

| |

v v

STUDENT SERVICE QWEN/GROQ

| |

v v

DATABASE MCP TOOLS

|

v

STUDENT SERVICE

|

v

DATABASE

|

v

TOOL RESULT

|

v

AI

|

v

USER



37\. Final Note



This project demonstrates how a traditional student management

system can be extended with an AI interface.



The important concept is not only the chatbot.



The important concept is the integration of:



Frontend

\+

FastAPI

\+

Business Logic

\+

Database

\+

MCP

\+

AI



This makes the system easier for users to interact with while

keeping the underlying student data and operations controlled

by the application.

