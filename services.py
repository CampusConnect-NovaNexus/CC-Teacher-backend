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
    
    # First increment total classes
    course.increment_total_classes()
    db.session.flush()  # Ensure the increment is saved
    
    # Then add attendance records
    db.session.add_all(attendance_records)
    db.session.commit()
    
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
    
    # Always calculate total classes from attendance records
    total_classes = get_total_classes(student.course_code, start_date, end_date)
    
    # Get attended classes
    attended_classes = query.count()
    
    # Calculate percentage
    attendance_percentage = (attended_classes / total_classes * 100) if total_classes != 0 else 0
    
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
    
# get attendance stats for a course
def get_course_attendance_stats(course_code, start_date=None, end_date=None):
    """Get attendance statistics for a course"""
    # Base query for attendance records
    query = Attendance.query.filter(Attendance.student_id.in_([s._id for s in Teacher.query.get(course_code).students]))
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Attendance.class_date >= start_date)
    if end_date:
        query = query.filter(Attendance.class_date <= end_date)
    
    # Get total classes in the date range
    total_classes = query.distinct(Attendance.class_date).count()
    
    # Get attended classes
    attended_classes = query.count()
    # get total students
    total_students = len(Teacher.query.get(course_code).students)
    
    # Calculate actual possible attendance (accounting for students who joined later)
    total_possible_attendance = 0
    for student in Teacher.query.get(course_code).students:
        student_attendance = Attendance.query.filter(
            Attendance.student_id == student._id,
            Attendance.class_date >= (start_date or datetime.min.replace(tzinfo=timezone.utc)),
            Attendance.class_date <= (end_date or datetime.max.replace(tzinfo=timezone.utc))
        ).count()
        total_possible_attendance += student_attendance
    
    attendance_percentage = (attended_classes / total_possible_attendance * 100) if total_possible_attendance > 0 else 0
    
    return {
        'course_code': course_code,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'attendance_percentage': round(attendance_percentage, 2),
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None,
        'total_students': total_students
    }

def get_total_classes(course_code, start_date=None, end_date=None):
    """Helper function to get total classes consistently"""
    query = Attendance.query.filter(
        Attendance.student_id.in_([s._id for s in Teacher.query.get(course_code).students])
    )
    if start_date:
        query = query.filter(Attendance.class_date >= start_date)
    if end_date:
        query = query.filter(Attendance.class_date <= end_date)
    return query.distinct(Attendance.class_date).count()

# fetch student having <75% attendance
def get_low_attendance_students(course_code, start_date=None, end_date=None):
    """Return students with <75% attendance in a course"""
    # Fetch the course
    course = Teacher.query.get(course_code)
    if not course:
        return {'error': 'Course not found'}, 404

    # Get all student IDs in the course
    student_ids = [student._id for student in course.students]

    # Base attendance query with date filters
    attendance_query = Attendance.query.filter(
        Attendance.student_id.in_(student_ids)
    )
    # Apply date filters
    if start_date:
        attendance_query = attendance_query.filter(Attendance.class_date >= start_date)
    if end_date:
        attendance_query = attendance_query.filter(Attendance.class_date <= end_date)

    # Get total distinct classes in date range
    total_classes = attendance_query.with_entities(Attendance.class_date).distinct().count()

    # Calculate attendance for each student
    low_attendance = []
    for student in course.students:
        # Get student's attendance count within date range
        attended = attendance_query.filter(
            Attendance.student_id == student._id
        ).count()

        # Calculate percentage
        percentage = (attended / total_classes * 100) if total_classes > 0 else 0
        
        if percentage < 75:
            low_attendance.append({
                'student_id': student._id,
                'attendance_percentage': round(percentage, 2)
            })

    return {
        'course_code': course_code,
        'total_classes': total_classes,
        'students_with_low_attendance': low_attendance,
        'total_students': len(course.students),
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None
    }
    
# Get attendance percentage of every student in a course
def get_course_attendance_percentage(course_code, start_date=None, end_date=None):
    """Get attendance percentage of every student in a course"""
    # Base query for attendance records
    query = Attendance.query.filter(Attendance.student_id.in_([s._id for s in Teacher.query.get(course_code).students]))
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Attendance.class_date >= start_date)
    if end_date:
        query = query.filter(Attendance.class_date <= end_date)
    
    # Get total classes in the date range
    total_classes = query.distinct(Attendance.class_date).count()
    
    # Get Total students
    total_students = len(Teacher.query.get(course_code).students)
    
    # Get attended classes
    attended_classes = query.count()
    
    # Calculate actual possible attendance (accounting for students who joined later)
    total_possible_attendance = 0
    for student in Teacher.query.get(course_code).students:
        student_attendance = Attendance.query.filter(
            Attendance.student_id == student._id,
            Attendance.class_date >= (start_date or datetime.min.replace(tzinfo=timezone.utc)),
            Attendance.class_date <= (end_date or datetime.max.replace(tzinfo=timezone.utc))
        ).count()
        total_possible_attendance += student_attendance
    
    attendance_percentage = (attended_classes / total_possible_attendance * 100) if total_possible_attendance > 0 else 0
    
    return {
        'course_code': course_code,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'attendance_percentage': round(attendance_percentage, 2),
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None,
        'total_students': total_students
    }