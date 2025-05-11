# Teacher Backend API Documentation

This document provides detailed information about the Teacher Backend API endpoints, their request/response formats, and data models.

## Base URL
All API endpoints are relative to the base URL of the teacher backend service.

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
