
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
import uuid
from datetime import datetime, timezone

db = SQLAlchemy()

class Teacher(db.Model):
    __tablename__ = 'teacher'
    
    course_code = db.Column(db.String(10), primary_key=True)
    Teacher = db.Column(ARRAY(db.String(50)), nullable=False)
    TA = db.Column(ARRAY(db.String(50)), nullable=False)
    total_classes = db.Column(db.Integer, default=0)

    # Relationship with students
    students = db.relationship('Student', backref='course', lazy=True, cascade='all, delete-orphan')

    def __init__(self, course_code, Teacher, TA):
        self.course_code = course_code
        self.Teacher = Teacher
        self.TA = TA
        self.total_classes = 0

    def increment_total_classes(self):
        self.total_classes += 1
        db.session.commit()

    def json(self):
        return {
            'course_code': self.course_code,
            'Teacher': self.Teacher,
            'TA': self.TA,
            'total_classes': self.total_classes
        }

class Student(db.Model):
    __tablename__ = 'student'
    
    _id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_code = db.Column(db.String(10), db.ForeignKey('teacher.course_code', ondelete='CASCADE'), nullable=False)
    roll_no = db.Column(db.String(12), nullable=False)
    name = db.Column(db.String(70), nullable=False)

    # Relationship with attendance
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')

    # Add unique constraint for roll_no within a course
    __table_args__ = (
        db.UniqueConstraint('course_code', 'roll_no', name='uix_course_roll'),
    )

    def __init__(self, course_code, roll_no, name):
        self.course_code = course_code
        self.roll_no = roll_no
        self.name = name

    def json(self):
        return {
            'id': self._id,
            'course_code': self.course_code,
            'roll_no': self.roll_no,
            'name': self.name
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('student._id', ondelete='CASCADE'), nullable=False)
    class_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Add index for faster queries
    __table_args__ = (
        db.Index('idx_attendance_student_date', 'student_id', 'class_date'),
    )

    def __init__(self, student_id, class_date=None):
        self.student_id = student_id
        self.class_date = class_date or datetime.now(timezone.utc)

    def json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'class_date': self.class_date.isoformat() if self.class_date else None
        }

        
