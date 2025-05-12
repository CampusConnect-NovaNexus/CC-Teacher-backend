from flask import Blueprint, request, jsonify
from services import *
from sqlalchemy import func
from models import *

# Create a Blueprint
teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is running'})

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
# Add student in a course
@teacher_bp.route('/courses/<course_code>/students', methods=['POST'])
def add_student(course_code):
    """Add a student to a course"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'roll_no' not in data:
        return jsonify({'error': 'student details are required'}), 400
    
    student_name = data['name']
    student_roll_no = data['roll_no']

    try:
        # Add student to course
        add_student_to_course(student_name, student_roll_no, course_code)
        return jsonify({'message': 'Student added to course'}), 201
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

# Return attendance record for a course
@teacher_bp.route('/attendance/stats/course/<course_code>', methods=['GET'])
def get_attendance_stats_for_course(course_code):
    """Get attendance statistics for a course"""
    try:
        # Parse date parameters if provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        stats = get_course_attendance_stats(course_code, start_date, end_date)
        return jsonify(stats), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/attendance/<course_code>/low', methods=['GET'])
def get_low_attendance(course_code):
    """Get students with low attendance"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        stats = get_low_attendance_students(course_code, start_date, end_date)
        return jsonify(stats), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Get attendance percentage of every student in a course
@teacher_bp.route('/attendance/stats/course/<course_code>/percentage', methods=['GET'])
def get_course_attendance_percentage_students(course_code):
    """Get attendance percentage of every student in a course"""
    try:
        # Parse date parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        start_date = None
        end_date = None

        # Validate date formats
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO 8601 format.'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO 8601 format.'}), 400

        # Get course and validate existence
        course = Teacher.query.get(course_code)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        # Get all students in course
        students = course.students
        student_ids = [s._id for s in students]

        # Build base attendance query
        attendance_query = Attendance.query.filter(
            Attendance.student_id.in_(student_ids)
        )

        # Apply date filters
        if start_date:
            attendance_query = attendance_query.filter(Attendance.class_date >= start_date)
        if end_date:
            attendance_query = attendance_query.filter(Attendance.class_date <= end_date)

        # Get total distinct classes in date range
        total_classes = get_total_classes(course_code, start_date, end_date)

        # Calculate attendance for each student
        student_stats = []
        for student in students:
            # Get student's attendance count
            attended = attendance_query.filter(
                Attendance.student_id == student._id
            ).count()

            # Calculate percentage
            percentage = (attended / total_classes * 100) if total_classes > 0 else 0
            
            student_stats.append({
                # 'student_id': student._id,
                'student_name': student.name,
                'roll_no': student.roll_no,
                'attendance_percentage': round(percentage, 2),
                'attended_classes': attended,
            })

        return jsonify({
            'course_code': course_code,
            'total_students': len(students),
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'students': student_stats,
            'total_classes': total_classes
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/courses/<course_code>/ta', methods=['POST'])
def add_ta(course_code):
    """Add a TA to a course"""
    data = request.get_json()
    if not data or 'ta_email' not in data:
        return jsonify({'error': 'ta_email is required'}), 400
    ta_email = data['ta_email']
    try:
        updated_course = add_ta_to_course(course_code, ta_email)
        return jsonify(updated_course), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@teacher_bp.route('/courses/<course_code>/ta', methods=['DELETE'])
def delete_ta(course_code):
    """Remove a TA from a course"""
    data = request.get_json()
    if not data or 'ta_email' not in data:
        return jsonify({'error': 'ta_email is required'}), 400
    ta_email = data['ta_email']
    try:
        updated_course = remove_ta_from_course(course_code, ta_email)
        return jsonify(updated_course), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400