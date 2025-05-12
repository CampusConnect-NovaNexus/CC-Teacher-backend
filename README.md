# Teacher Service - CampusConnect

This service handles the teacher-specific functionality for the CampusConnect platform, including course management, student attendance tracking, and teaching assistant (TA) administration.

## Technologies
- Python 3.x
- Flask (Web Framework)
- PostgreSQL with SQLAlchemy ORM
- Flask-Migrate (Database Migrations)
- Waitress (Production WSGI Server) 
- Docker for containerization

## Features
- Attendance tracking and management
- Course management for teachers
- TA administration
- Low attendance detection and reporting
- Attendance statistics and analytics

## Base URL
All API endpoints are prefixed with `/api/teacher`

## API Endpoints

### 1. Test Server
```http
GET /test
```
Checks if the server is running.

**Response:**
```json
{
    "message": "Server is running"
}
```

### 2. Get Teacher Courses
```http
GET /courses?email={teacher_email}
```
Retrieves all courses where the specified email is either a teacher or TA.

**Query Parameters:**
- `email` (required): Email address of the teacher/TA

**Response:**
```json
[
    {
        "course_code": "string",
        "Teacher": ["string"],
        "TA": ["string"],
        "total_classes": number
    }
]
```

### 3. Get Course Students
```http
GET /courses/{course_code}/students
```
Retrieves all students enrolled in a specific course.

**Path Parameters:**
- `course_code` (required): Code of the course

**Response:**
```json
[
    {
        "id": "string",
        "course_code": "string",
        "roll_no": "string",
        "name": "string"
    }
]
```

### 4. Mark Attendance
```http
POST /attendance
```
Marks attendance for multiple students in a course.

**Request Body:**
```json
{
    "course_code": "string",
    "roll_numbers": ["string"]
}
```

**Response:**
```json
[
    {
        "id": "string",
        "student_id": "string",
        "class_date": "string (ISO format)"
    }
]
```

### 5. Get Student Attendance Stats
```http
GET /attendance/stats/{student_id}
```
Retrieves attendance statistics for a specific student.

**Path Parameters:**
- `student_id` (required): ID of the student

**Query Parameters:**
- `start_date` (optional): Start date in ISO format
- `end_date` (optional): End date in ISO format

**Response:**
```json
{
    "student_id": "string",
    "student_name": "string",
    "roll_no": "string",
    "course_code": "string",
    "total_classes": number,
    "attended_classes": number,
    "attendance_percentage": number,
    "start_date": "string (ISO format)",
    "end_date": "string (ISO format)"
}
```

### 6. Get Course Attendance Stats
```http
GET /attendance/stats/course/{course_code}
```
Retrieves attendance statistics for an entire course.

**Path Parameters:**
- `course_code` (required): Code of the course

**Query Parameters:**
- `start_date` (optional): Start date in ISO format
- `end_date` (optional): End date in ISO format

**Response:**
```json
{
    "course_code": "string",
    "total_classes": number,
    "attended_classes": number,
    "attendance_percentage": number,
    "start_date": "string (ISO format)",
    "end_date": "string (ISO format)",
    "total_students": number
}
```

### 7. Get Low Attendance Students
```http
GET /attendance/{course_code}/low
```
Retrieves list of students with attendance below 75% in a course.

**Path Parameters:**
- `course_code` (required): Code of the course

**Query Parameters:**
- `start_date` (optional): Start date in ISO format
- `end_date` (optional): End date in ISO format

**Response:**
```json
{
    "course_code": "string",
    "total_classes": number,
    "students_with_low_attendance": [
        {
            "student_id": "string",
            "attendance_percentage": number
        }
    ],
    "total_students": number,
    "start_date": "string (ISO format)",
    "end_date": "string (ISO format)"
}
```

### 8. Get Course Attendance Percentage
```http
GET /attendance/stats/course/{course_code}/percentage
```
Retrieves detailed attendance percentage for each student in a course.

**Path Parameters:**
- `course_code` (required): Code of the course

**Query Parameters:**
- `start_date` (optional): Start date in ISO format
- `end_date` (optional): End date in ISO format

**Response:**
```json
{
    "course_code": "string",
    "total_students": number,
    "start_date": "string (ISO format)",
    "end_date": "string (ISO format)",
    "students": [
        {
            "student_name": "string",
            "roll_no": "string",
            "attendance_percentage": number,
            "attended_classes": number
        }
    ],
    "total_classes": number
}
```

### 9. Add TA to Course
```http
POST /courses/{course_code}/ta
```
Adds a TA to a course.

**Path Parameters:**
- `course_code` (required): Code of the course

**Request Body:**
```json
{
    "ta_email": "string"
}
```

**Response:**
```json
{
    "course_code": "string",
    "Teacher": ["string"],
    "TA": ["string"],
    "total_classes": number
}
```

**Error Responses:**
- 400 if `ta_email` is missing or TA already exists or course not found.

### 10. Remove TA from Course
```http
DELETE /courses/{course_code}/ta
```
Removes a TA from a course.

**Path Parameters:**
- `course_code` (required): Code of the course

**Request Body:**
```json
{
    "ta_email": "string"
}
```

**Response:**
```json
{
    "course_code": "string",
    "Teacher": ["string"],
    "TA": ["string"],
    "total_classes": number
}
```

**Error Responses:**
- 400 if `ta_email` is missing or TA not found or course not found.

## Data Models

### Teacher
```json
{
    "course_code": "string (primary key)",
    "Teacher": ["string"],
    "TA": ["string"],
    "total_classes": number
}
```

### Student
```json
{
    "id": "string (primary key)",
    "course_code": "string (foreign key)",
    "roll_no": "string",
    "name": "string"
}
```

### Attendance
```json
{
    "id": "string (primary key)",
    "student_id": "string (foreign key)",
    "class_date": "string (ISO format)"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "Error message"
}
```

### 404 Not Found
```json
{
    "error": "Error message"
}
```

### 500 Internal Server Error
```json
{
    "error": "Error message"
}
```

## Notes
- All dates are in ISO format
- All IDs are UUID strings
- Course codes are 10 characters long
- Roll numbers are 12 characters long
- Student names are up to 70 characters long
- Teacher/TA emails are up to 50 characters long
- Attendance percentage is calculated as (attended_classes / total_classes * 100)
- Low attendance is defined as attendance percentage below 75%
