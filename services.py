from flask import request, jsonify, make_response
from models import *
from datetime import datetime, timezone
import requests
from sqlalchemy import func

def get_teacher_courses(email):
    """Get all courses where the given email is either a teacher or TA"""
    courses = Teacher.query.filter(
        (Teacher.Teacher.contains([email])) | 
        (Teacher.TA.contains([email]))
    ).all()
    return [course.json() for course in courses]

def get_course_students(course_code):
    """Get all students enrolled in a specific course"""
    students = Student.query.filter_by(course_code=course_code).all()
    return [student.json() for student in students]

def mark_attendance(course_code, roll_numbers):
    """Mark attendance for multiple students in a course"""
    current_time = datetime.now(timezone.utc)
    attendance_records = []
    
    # Get the course and increment total classes
    course = Teacher.query.get(course_code)
    if not course:
        raise ValueError(f"Course {course_code} not found")
    
    # Get all students with the given roll numbers in the course
    students = Student.query.filter(
        Student.course_code == course_code,
        Student.roll_no.in_(roll_numbers)
    ).all()
    
    # Create attendance records
    for student in students:
        attendance = Attendance(
            student_id=student._id,
            class_date=current_time
        )
        attendance_records.append(attendance)
    
    # Add all records to database and increment total classes
    db.session.add_all(attendance_records)
    course.increment_total_classes()
    
    return [record.json() for record in attendance_records]

def get_student_attendance_stats(student_id, start_date=None, end_date=None):
    """Get attendance statistics for a student"""
    # Base query for attendance records
    query = Attendance.query.filter(Attendance.student_id == student_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Attendance.class_date >= start_date)
    if end_date:
        query = query.filter(Attendance.class_date <= end_date)
    
    # Get the student and their course
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student {student_id} not found")
    
    course = Teacher.query.get(student.course_code)
    if not course:
        raise ValueError(f"Course {student.course_code} not found")
    
    # Get total classes in the date range
    total_classes = course.total_classes
    if start_date or end_date:
        # If date range is specified, count classes in that range
        total_classes = Attendance.query.filter(
            Attendance.student_id.in_([s._id for s in course.students]),
            Attendance.class_date >= (start_date or datetime.min.replace(tzinfo=timezone.utc)),
            Attendance.class_date <= (end_date or datetime.max.replace(tzinfo=timezone.utc))
        ).distinct(Attendance.class_date).count()
    
    # Get attended classes
    attended_classes = query.count()
    
    # Calculate percentage
    attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0
    
    return {
        'student_id': student_id,
        'student_name': student.name,
        'roll_no': student.roll_no,
        'course_code': student.course_code,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'attendance_percentage': round(attendance_percentage, 2),
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None
    }
    
