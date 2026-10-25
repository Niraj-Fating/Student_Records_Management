"""
SQLAlchemy ORM Models Module
Defines SQLite database tables and schema for student records.
"""
from sqlalchemy import Column, Integer, String, Date
from database import Base


class Student(Base):
    """
    Student Database Model
    Represents the 'students' table in SQLite.
    
    Fields:
      - student_id: Primary key (Unique student ID)
      - name: Full name of student (Mandatory)
      - date_of_birth: Date of birth (Mandatory)
      - email: Contact email address (Mandatory: email or phone)
      - phone: Contact phone number (Mandatory: email or phone)
      - course: Enrolled course (Optional)
      - address: Residential address (Optional)
      - enrollment_date: Date of enrollment (Optional)
    """
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(120), nullable=True, index=True)
    phone = Column(String(30), nullable=True)
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"<Student(student_id={self.student_id}, name='{self.name}', course='{self.course}')>"
