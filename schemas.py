"""
Pydantic Schemas Module
Defines request validation and response serialisation models for Student records.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class StudentBase(BaseModel):
    """Base fields shared across student schemas."""
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the student")
    date_of_birth: date = Field(..., description="Date of birth in YYYY-MM-DD format")
    email: Optional[EmailStr] = Field(default=None, description="Valid email address (e.g., student@example.com)")
    phone: Optional[str] = Field(default=None, max_length=30, description="Contact phone number")
    course: Optional[str] = Field(default=None, max_length=100, description="Enrolled course name")
    address: Optional[str] = Field(default=None, max_length=255, description="Residential address")
    enrollment_date: Optional[date] = Field(default=None, description="Enrollment date in YYYY-MM-DD format")

    @model_validator(mode="after")
    def validate_contact_information(self):
        """
        Ensures that at least one contact channel (email or phone) is provided.
        Raises ValueError which FastAPI translates into 422 Unprocessable Entity.
        """
        if not self.email and not self.phone:
            raise ValueError("At least one contact method ('email' or 'phone') must be provided.")
        return self


class StudentCreate(StudentBase):
    """
    Schema for creating a new student record (POST /students).
    student_id is optional: if omitted, database auto-assigns an autoincrement ID.
    If provided, it will be validated and used as the unique primary key.
    """
    student_id: Optional[int] = Field(
        default=None,
        description="Optional unique student ID. If omitted, the database auto-generates one."
    )


class StudentUpdate(BaseModel):
    """
    Schema for updating an existing student (PUT / PATCH /students/{student_id}).
    All fields are optional to support partial updates.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = Field(default=None, description="Date of birth in YYYY-MM-DD format")
    email: Optional[EmailStr] = Field(default=None, description="Valid email address")
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    enrollment_date: Optional[date] = Field(default=None, description="Enrollment date in YYYY-MM-DD format")


class StudentResponse(BaseModel):
    """
    Schema for returning student record data in API responses.
    """
    student_id: int
    name: str
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class AIQueryRequest(BaseModel):
    """Schema for querying local Ollama AI regarding student data."""
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language question about student records",
        examples=["How many students are enrolled?", "List all students taking Data Science."]
    )
    model: Optional[str] = Field(
        default="llama3.2:1b",
        description="Name of the local Ollama model to invoke"
    )


class AIQueryResponse(BaseModel):
    """Response returned from the AI assistant endpoint."""
    query: str
    response: str
    grounded_record_count: int
    model: str

