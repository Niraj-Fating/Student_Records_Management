# Students Database CRUD Application

> **Python Backend Development Internship Project**  
> **Company:** EWB Edu Tech Pvt. Ltd.  
> **Tech Stack:** Python 3.10+, FastAPI, SQLite, SQLAlchemy, Pydantic, Uvicorn, Ollama  

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Database Schema & Architecture](#-database-schema--architecture)
4. [Prerequisites](#-prerequisites)
5. [Installation & Setup](#-installation--setup)
6. [Running the Application](#-running-the-application)
7. [API Documentation & Endpoints](#-api-documentation--endpoints)
8. [Automated Testing](#-automated-testing)
9. [Optional Local AI Extension (Ollama)](#-optional-local-ai-extension-ollama)
10. [Project Review Checklist](#-project-review-checklist)
11. [Security & Best Practices](#-security--best-practices)

---

## 🎯 Project Overview

The **Students Database CRUD Application** is a high-performance local backend system built using **FastAPI** and **SQLite** (via SQLAlchemy ORM). It enables educational institutions to manage student records through full Create, Read, Update, and Delete (CRUD) operations with persistent storage, strict Pydantic input validation, and comprehensive error handling.

An **optional Local AI extension** powered by **Ollama** (`llama3.2:1b`) allows users to query student records in natural language without exposing the database to direct or arbitrary SQL execution.

---

## ✨ Key Features

- **Full CRUD Operations:** Add, list, filter, inspect, update, and delete student records.
- **Relational Persistence:** SQLite database (`students.db`) with SQLAlchemy ORM models.
- **Strict Data Validation:**
  - Mandatory fields validated with Pydantic v2.
  - Contact rule enforced: at least one contact channel (`email` or `phone`) must be supplied.
  - Automatic `422 Unprocessable Entity` for malformed dates (`YYYY-MM-DD`) and invalid email formats.
- **Error Handling:** Clean, informative HTTP `404 Not Found` and `400 Bad Request` responses for missing records or duplicate IDs/emails.
- **Filtering & Pagination:** Filter student lists by course name or student name, with `skip` and `limit` pagination.
- **Interactive API Documentation:** Built-in Swagger UI (`/docs`) and ReDoc (`/redoc`).
- **Grounded AI Queries:** Natural language Q&A endpoint (`POST /ask`) grounded strictly on retrieved records.

---

## 🗄️ Database Schema & Architecture

### Student Record Model

| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | Integer | Primary Key, Indexed, Autoincrement | Unique student identifier |
| `name` | String(100) | Mandatory | Full student name |
| `date_of_birth` | Date | Mandatory | Birth date (`YYYY-MM-DD`) |
| `email` | String(120) | Indexed, Unique | Contact email (Mandatory: email or phone) |
| `phone` | String(30) | Optional | Contact phone number |
| `course` | String(100) | Indexed | Enrolled course |
| `address` | String(255) | Optional | Residential address |
| `enrollment_date`| Date | Optional | Date of enrollment (`YYYY-MM-DD`) |

### Project File Structure

```text
EWB_Project/
├── database.py         # SQLite engine, SessionLocal, and get_db dependency
├── models.py           # SQLAlchemy Student ORM model
├── schemas.py          # Pydantic validation schemas (Create, Update, Response, AI)
├── main.py             # FastAPI application routes & CRUD endpoints
├── test_crud.py        # Automated integration test suite
├── requirements.txt    # Project dependencies
├── .gitignore          # Git ignore rules (.venv, *.db, __pycache__)
└── README.md           # Comprehensive documentation
```

---

## ⚙️ Prerequisites

- **Python:** 3.10 or higher (Tested with Python 3.13)
- **Git:** For version control
- *(Optional)* **Ollama:** If using the local AI query extension ([Download Ollama](https://ollama.com))

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd EWB_Project
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

Start the local ASGI development server with Uvicorn:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Once running, the application will be accessible at:
- **Root Health Check:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Documentation & Endpoints

### 1. Create a Student Record
- **Method:** `POST /students`
- **Status:** `201 Created`
- **Request Body:**
```json
{
  "name": "Priya Patel",
  "date_of_birth": "2003-04-12",
  "email": "priya.patel@example.com",
  "phone": "+91-9876543210",
  "course": "Data Science",
  "address": "Ahmedabad, Gujarat",
  "enrollment_date": "2023-07-15"
}
```
- **Response (201):**
```json
{
  "student_id": 1,
  "name": "Priya Patel",
  "date_of_birth": "2003-04-12",
  "email": "priya.patel@example.com",
  "phone": "+91-9876543210",
  "course": "Data Science",
  "address": "Ahmedabad, Gujarat",
  "enrollment_date": "2023-07-15"
}
```

### 2. List All Students (with Filtering & Pagination)
- **Method:** `GET /students`
- **Query Parameters:**
  - `course` (optional): Filter by course substring (e.g. `?course=Data`)
  - `name` (optional): Filter by name substring (e.g. `?name=Priya`)
  - `skip` (optional, default `0`): Pagination offset
  - `limit` (optional, default `100`): Maximum records to return
- **Response (200):**
```json
[
  {
    "student_id": 1,
    "name": "Priya Patel",
    "date_of_birth": "2003-04-12",
    "email": "priya.patel@example.com",
    "phone": "+91-9876543210",
    "course": "Data Science",
    "address": "Ahmedabad, Gujarat",
    "enrollment_date": "2023-07-15"
  }
]
```

### 3. View a Specific Student Profile
- **Method:** `GET /students/{student_id}`
- **Response (200):** Returns student record.
- **Response (404):**
```json
{
  "detail": "Student with ID 99 not found."
}
```

### 4. Update Student Details
- **Method:** `PUT /students/{student_id}` or `PATCH /students/{student_id}`
- **Request Body (Partial Update):**
```json
{
  "course": "Advanced Data Science & AI",
  "address": "Gandhinagar, Gujarat"
}
```
- **Response (200):** Updated student object.

### 5. Delete a Student
- **Method:** `DELETE /students/{student_id}`
- **Response (200):**
```json
{
  "message": "Student with ID 1 has been successfully deleted."
}
```

---

## 🧪 Automated Testing

A complete integration test suite is included in [`test_crud.py`](file:///c:/Users/niraj/OneDrive/Desktop/EWB_Project/test_crud.py), covering:
1. `POST /students` creation.
2. `GET /students` listing and filtering.
3. `GET /students/{id}` retrieval.
4. `PATCH /students/{id}` and `PUT /students/{id}` updates.
5. `DELETE /students/{id}` deletion.
6. `404 Not Found` validation on non-existent records.
7. `422 Unprocessable Entity` validation on malformed dates, invalid emails, and missing contact information.
8. `POST /ask` Ollama offline fallback (`503`) and response grounding.

### Run Tests:
```bash
python test_crud.py
```

**Expected Output:**
```text
ALL CRUD, VALIDATION, AND AI TESTS PASSED!
```

---

## 🤖 Optional Local AI Extension (Ollama)

The application includes an optional natural language Q&A endpoint grounded in your student records.

- **Endpoint:** `POST /ask`
- **Request Body:**
```json
{
  "query": "How many students are enrolled in Data Science?",
  "model": "llama3.2:1b"
}
```

### How to Enable Ollama:
1. Install Ollama from [https://ollama.com](https://ollama.com).
2. Start the local server:
   ```bash
   ollama serve
   ```
3. Pull the lightweight model:
   ```bash
   ollama run llama3.2:1b
   ```
4. Query the API via `POST /ask` or through Swagger UI (`/docs`).

> **Security Note:** The AI model is **never** given direct SQL access. Records are retrieved safely by backend Python ORM logic first, serialized to JSON, and passed as read-only context in the prompt.

---

## ✅ Project Review Checklist

- [x] **Create:** Add new student records to SQLite with validation.
- [x] **Read:** List all students and filter by course or name; inspect individual profiles.
- [x] **Update:** Modify student details via `PUT` and `PATCH`.
- [x] **Delete:** Permanently remove records by ID.
- [x] **Data Persistence:** SQLite database persists records across server restarts.
- [x] **Error Handling:** Clean `404 Not Found`, `400 Bad Request`, and `422 Unprocessable Entity`.
- [x] **Code Organization:** Modular design (`database.py`, `models.py`, `schemas.py`, `main.py`).
- [x] **Optional AI:** Grounded responses using Ollama without direct SQL execution.
- [x] **Reproducible:** Self-contained `requirements.txt` and automated test script.

---

## 🔒 Security & Best Practices

1. **No Direct SQL Execution for AI:** Prompts only receive sanitized, read-only JSON snapshots.
2. **Prepared Statements / ORM:** SQLAlchemy prevents SQL injection across all CRUD operations.
3. **Contact Rule Invariant:** Updates and creations must preserve at least one valid contact method (`email` or `phone`).
4. **Environment Isolation:** All temporary database files and virtual environments are excluded via `.gitignore`.
5. **No Hardcoded Secrets:** Application uses dummy educational data and local database files.

---

**Developed for EWB Edu Tech Pvt. Ltd. Internship Program**
