"""
Main FastAPI Application Module
Implements CRUD API routes for Student management.
"""
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import json
import os
import requests

import models
import schemas
from database import engine, get_db

# Create database tables automatically upon startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Students Database CRUD API",
    description="A robust backend system to manage student records with SQLite, SQLAlchemy, and FastAPI.",
    version="1.0.0",
)


@app.get("/", tags=["General"], summary="Root Health Check & Info")
def read_root():
    """Returns welcoming information and quick links to documentation and endpoints."""
    return {
        "status": "online",
        "service": "Students Database CRUD API",
        "documentation": "/docs",
        "openapi_spec": "/openapi.json",
        "endpoints": {
            "create_student": "POST /students",
            "get_all_students": "GET /students",
            "get_student": "GET /students/{student_id}",
            "update_student": "PUT or PATCH /students/{student_id}",
            "delete_student": "DELETE /students/{student_id}",
            "ask_ai": "POST /ask (Natural Language queries via local Ollama)",
        }
    }


# ==========================================
# 1. CREATE: POST /students
# ==========================================
@app.post(
    "/students",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"],
    summary="Create and save a new student record"
)
def create_student(
    student_in: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new student record in the SQLite database.
    - Validates mandatory fields: name, date_of_birth, and at least one of (email, phone).
    - Checks for primary key conflict if a custom student_id is provided.
    - Checks for duplicate email address if provided.
    """
    # Check if student_id is manually specified and already exists
    if student_in.student_id is not None:
        existing_student = db.query(models.Student).filter(
            models.Student.student_id == student_in.student_id
        ).first()
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with ID {student_in.student_id} already exists."
            )

    # Check for email uniqueness if provided
    if student_in.email:
        existing_email = db.query(models.Student).filter(
            models.Student.email == student_in.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student with email '{student_in.email}' already exists."
            )

    student_data = student_in.model_dump(exclude_unset=True)
    new_student = models.Student(**student_data)

    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


# ==========================================
# 2. READ ALL: GET /students (with filtering)
# ==========================================
@app.get(
    "/students",
    response_model=List[schemas.StudentResponse],
    tags=["Students"],
    summary="Retrieve all students with optional course/name filtering"
)
def get_students(
    course: Optional[str] = Query(None, description="Filter students by course (case-insensitive substring)"),
    name: Optional[str] = Query(None, description="Filter students by name (case-insensitive substring)"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Lists student records from the SQLite database.
    Supports filtering by course and name, as well as pagination via skip and limit.
    """
    query = db.query(models.Student)

    if course:
        query = query.filter(models.Student.course.ilike(f"%{course}%"))
    if name:
        query = query.filter(models.Student.name.ilike(f"%{name}%"))

    students = query.offset(skip).limit(limit).all()
    return students


# ==========================================
# 3. READ ONE: GET /students/{student_id}
# ==========================================
@app.get(
    "/students/{student_id}",
    response_model=schemas.StudentResponse,
    tags=["Students"],
    summary="View a specific student profile by ID"
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves a single student's record by their unique student_id.
    Returns 404 Not Found if the student does not exist.
    """
    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return student


# Helper function for updates
def _apply_student_update(
    student_id: int,
    student_update: schemas.StudentUpdate,
    db: Session
) -> models.Student:
    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )

    update_dict = student_update.model_dump(exclude_unset=True)

    # Check for email uniqueness if updated
    if "email" in update_dict and update_dict["email"]:
        existing_email = db.query(models.Student).filter(
            models.Student.email == update_dict["email"],
            models.Student.student_id != student_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{update_dict['email']}' is already in use by another student."
            )

    for field, value in update_dict.items():
        setattr(student, field, value)

    # Ensure at least one contact method remains valid
    if not student.email and not student.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student must retain at least one contact method ('email' or 'phone')."
        )

    db.commit()
    db.refresh(student)
    return student


# ==========================================
# 4. UPDATE: PUT & PATCH /students/{student_id}
# ==========================================
@app.put(
    "/students/{student_id}",
    response_model=schemas.StudentResponse,
    tags=["Students"],
    summary="Update an existing student's details (PUT)"
)
def update_student_put(
    student_id: int,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    """Updates student fields; returns 404 if the student_id is not found."""
    return _apply_student_update(student_id, student_update, db)


@app.patch(
    "/students/{student_id}",
    response_model=schemas.StudentResponse,
    tags=["Students"],
    summary="Partially update an existing student's details (PATCH)"
)
def update_student_patch(
    student_id: int,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    """Partially updates student fields; returns 404 if the student_id is not found."""
    return _apply_student_update(student_id, student_update, db)


# ==========================================
# 5. DELETE: DELETE /students/{student_id}
# ==========================================
@app.delete(
    "/students/{student_id}",
    status_code=status.HTTP_200_OK,
    tags=["Students"],
    summary="Remove a student record from the database"
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Deletes a student record by ID.
    Returns 404 Not Found if the student_id is not found.
    """
    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )

    db.delete(student)
    db.commit()
    return {"message": f"Student with ID {student_id} has been successfully deleted."}


# ==========================================
# 6. LOCAL AI EXTENSION: POST /ask (Ollama)
# ==========================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_students_context(db: Session) -> str:
    """
    Retrieves all student records from the database using secure SQLAlchemy ORM logic
    and serializes them into structured JSON text.
    
    Security Constraint: The AI model is NEVER granted direct SQL execution access.
    Data is fetched strictly through backend Python queries, preventing SQL injection
    and unauthorized database modifications.
    """
    students = db.query(models.Student).all()
    if not students:
        return "No student records currently exist in the database."

    records = []
    for s in students:
        records.append({
            "student_id": s.student_id,
            "name": s.name,
            "date_of_birth": str(s.date_of_birth) if s.date_of_birth else None,
            "email": s.email,
            "phone": s.phone,
            "course": s.course,
            "address": s.address,
            "enrollment_date": str(s.enrollment_date) if s.enrollment_date else None,
        })
    return json.dumps(records, indent=2)


def query_local_ollama(prompt: str, model: str = "llama3.2:1b") -> str:
    """
    Sends the prompt along with student context to a locally running Ollama instance.
    Calls POST /api/generate on Ollama.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "").strip()


@app.post(
    "/ask",
    response_model=schemas.AIQueryResponse,
    tags=["AI Assistant"],
    summary="Ask natural language questions about student records (Local Ollama)"
)
def ask_ai(
    query_in: schemas.AIQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Accepts natural language questions (e.g. 'How many students are enrolled?', 'List students born after 2005').
    - Securely retrieves all database records via backend Python/ORM logic.
    - Grounding: Constructs a strict contextual prompt to ensure the response is grounded only in existing records.
    - Sends the context to the local Ollama instance (default model: `llama3.2:1b`).
    - Returns human-readable answers without allowing direct SQL execution.
    """
    student_count = db.query(models.Student).count()
    context_data = get_students_context(db)

    prompt = (
        "You are an intelligent database assistant for a Student Records System.\n"
        "Analyze the following student records provided in JSON format and answer the user's question accurately.\n\n"
        f"--- STUDENT DATABASE RECORDS ({student_count} records) ---\n"
        f"{context_data}\n"
        "--------------------------------------------------\n\n"
        "Guidelines:\n"
        "1. Base your answer STRICTLY on the records provided above.\n"
        "2. If the information requested is not present in the data, state clearly that it is not available.\n"
        "3. Keep the response concise, factual, and professional.\n\n"
        f"User Question: {query_in.query}\n"
        "Answer:"
    )

    try:
        ai_reply = query_local_ollama(prompt, model=query_in.model)
        return schemas.AIQueryResponse(
            query=query_in.query,
            response=ai_reply,
            grounded_record_count=student_count,
            model=query_in.model
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Could not connect to local Ollama service at '{OLLAMA_BASE_URL}'. "
                "To enable this optional AI feature: "
                "1. Download and install Ollama from https://ollama.com\n"
                "2. Start Ollama with `ollama serve`\n"
                f"3. Pull your desired model with `ollama run {query_in.model}`"
            )
        )
    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"An error occurred while communicating with Ollama: {str(exc)}"
        )

