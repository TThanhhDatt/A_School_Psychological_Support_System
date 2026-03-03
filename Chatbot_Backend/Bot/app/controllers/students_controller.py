from bson import ObjectId
from app.models.students_model import student_collection, student_helper, Student

# Create
def create_student(student: Student):
    student_dict = student.model_dump()
    result = student_collection.insert_one(student_dict)
    new_doc = student_collection.find_one({"_id": result.inserted_id})
    return student_helper(new_doc)

# Read all
def get_students():
    students = []
    for s in student_collection.find():
        students.append(student_helper(s))
    return students

# Read by ID
def get_student_by_id(student_id: str):
    student = student_collection.find_one({"_id": ObjectId(student_id)})
    if student:
        return student_helper(student)
    return None

# Update
def update_student(student_id: str, data: dict):
    result = student_collection.update_one(
        {"_id": ObjectId(student_id)}, {"$set": data}
    )
    return result.modified_count > 0

# Delete
def delete_student(student_id: str):
    result = student_collection.delete_one({"_id": ObjectId(student_id)})
    return result.deleted_count > 0