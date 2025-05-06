from sqlalchemy.orm import Session
from bot.services.user_service import UserService
from database.repositories.teacher_repo import TeacherRepository

class TeacherService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.teacher_repo = TeacherRepository(db)

    async def add_teacher(self, student_id, teacher_username):
        teacher = self.user_service.get_by_username(teacher_username)
        if not teacher:
            return None

        return self.teacher_repo.add_teacher(student_id, teacher.id)