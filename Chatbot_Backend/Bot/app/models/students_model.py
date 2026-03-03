from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, List
from app.database.mongo import db

# Định nghĩa schema đầu vào từ client
class Student(BaseModel):
    student_name: str
    student_id: str
    phq_progress: List[dict]
    stress_level: Optional[str] = None
    problem_detection: dict
    student_summary: dict
    deep_support_summary: Optional[dict]

# Schema trả ra có thêm _id
class StudentInDB(Student):
    id: str = Field(alias="_id")

# MongoDB collection
student_collection = db["students"]

# Helper để chuyển ObjectId thành string
def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "student_name": student["student_name"],
        "student_id": student["student_id"],
        "phq_progress": student["phq_progress"],
        "stress_level": student.get("stress_level"),
        "problem_detection": student.get("problem_detection"),
        "student_summary": student["student_summary"],
        "deep_support_summary": student["deep_support_summary"]
    }