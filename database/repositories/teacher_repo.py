from sqlalchemy.orm import Session
from database.models import TeacherStudent

class TeacherRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_teacher(self, student_id, teacher_id):
        relation = TeacherStudent(student_id=student_id, teacher_id=teacher_id)
        self.db.add(relation)
        self.db.commit()
        self.db.refresh(relation)
        return relation

    def get_student_teachers(self, student_id):
        return self.db.query(TeacherStudent).filter_by(student_id=student_id).all()

    def get_teacher_students(self, teacher_id):
        return self.db.query(TeacherStudent).filter_by(teacher_id=teacher_id).all()