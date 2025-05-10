from flask import Blueprint, request, jsonify
from services import get_teacher_courses, get_course_students, mark_attendance, get_student_attendance_stats
from datetime import datetime

# Create a Blueprint
teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get all courses for a teacher/TA"""
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        courses = get_teacher_courses(email)
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/courses/<course_code>/students', methods=['GET'])
def get_students(course_code):
    """Get all students enrolled in a course"""
    try:
        students = get_course_students(course_code)
        return jsonify(students), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/attendance', methods=['POST'])
def post_attendance():
    """Mark attendance for multiple students"""
    data = request.get_json()
    
    if not data or 'course_code' not in data or 'roll_numbers' not in data:
        return jsonify({'error': 'course_code and roll_numbers are required'}), 400
    
    course_code = data['course_code']
    roll_numbers = data['roll_numbers']
    
    if not isinstance(roll_numbers, list):
        return jsonify({'error': 'roll_numbers must be an array'}), 400
    
    try:
        attendance_records = mark_attendance(course_code, roll_numbers)
        return jsonify(attendance_records), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/attendance/stats/<student_id>', methods=['GET'])
def get_attendance_stats(student_id):
    """Get attendance statistics for a student"""
    try:
        # Parse date parameters if provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        stats = get_student_attendance_stats(student_id, start_date, end_date)
        return jsonify(stats), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
