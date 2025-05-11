# Campus Connect Teacher Backend API Documentation

## API Overview
This documentation provides details on the Campus Connect Teacher API endpoints, their usage, request parameters, and response formats. It is intended to help frontend developers integrate with the teacher-specific functionalities of the Campus Connect platform.

## Base URL
All API endpoints are prefixed with: `/api/teacher`

## Database Schema
The application uses PostgreSQL with the following models:

### Teacher Model
```
Teacher {
  course_code: string (primary key)
  Teacher: array of strings (emails)
  TA: array of strings (emails)
  total_classes: integer
}
```

### Student Model
```
Student {
  _id: string (UUID, primary key)
  course_code: string (foreign key to Teacher.course_code)
  roll_no: string
  name: string
}
```

### Attendance Model
```
Attendance {
  id: string (UUID, primary key)
  student_id: string (foreign key to Student._id)
  class_date: datetime
}
```

## API Endpoints

### 1. Server Status

#### Check Server Status
- **Endpoint**: `GET /test`
- **Description**: Verifies if the server is running
- **Response Example**:
  ```json
  {
    "message": "Server is running"
  }
  ```
- **Status Codes**:
  - `200 OK`: Server is operational

### 2. Teacher Profile Management

#### Get Teacher Profile
- **Endpoint**: `GET /profile`
- **Description**: Retrieves the profile information of the authenticated teacher.
- **Request**: None
- **Response**:
  ```json
  {
    "teacher_id": "TCH1001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "department": "Computer Science",
    "office_location": "Room 301, Block A"
  }
  ```
- **Status Codes**:
  - `200 OK`: Profile retrieved successfully.
  - `401 Unauthorized`: Authentication failed.
  - `404 Not Found`: Teacher profile not found.
  - `500 Internal Server Error`: Error retrieving profile.

#### Update Teacher Profile
- **Endpoint**: `PUT /profile`
- **Description**: Updates the profile information of the authenticated teacher.
- **Request Body**:
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "department": "Computer Science",
    "office_location": "Room 302, Block A"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Profile updated successfully",
    "teacher_id": "TCH1001"
  }
  ```
- **Status Codes**:
  - `200 OK`: Profile updated successfully.
  - `400 Bad Request`: Invalid input data.
  - `401 Unauthorized`: Authentication failed.
  - `500 Internal Server Error`: Error updating profile.

### 3. Course Management

#### Get Teacher Courses
- **Endpoint**: `GET /courses`
- **Description**: Retrieves all courses where the given email is either a teacher or TA
- **Query Parameters**:
  - `email` (required): Email address of the teacher/TA
- **Response Example**:
  ```json
  [
    {
      "course_code": "CS101",
      "Teacher": ["professor@example.com"],
      "TA": ["assistant@example.com"],
      "total_classes": 15
    },
    {
      "course_code": "CS202",
      "Teacher": ["professor@example.com"],
      "TA": ["assistant2@example.com"],
      "total_classes": 12
    }
  ]
  ```
- **Status Codes**:
  - `200 OK`: Courses retrieved successfully
  - `400 Bad Request`: Email parameter missing
  - `500 Internal Server Error`: Server error

#### Get Courses Taught by Teacher
- **Endpoint**: `GET /courses`
- **Description**: Retrieves a list of courses taught by the authenticated teacher.
- **Request**: None
- **Response**:
  ```json
  [
    {
      "course_code": "CS101",
      "course_name": "Introduction to Programming",
      "semester": "Fall 2024",
      "credits": 3
    },
    {
      "course_code": "CS202",
      "course_name": "Data Structures",
      "semester": "Fall 2024",
      "credits": 4
    }
  ]
  ```
- **Status Codes**:
  - `200 OK`: Courses retrieved successfully.
  - `401 Unauthorized`: Authentication failed.
  - `500 Internal Server Error`: Error retrieving courses.

#### Get Course Details
- **Endpoint**: `GET /courses/{course_code}`
- **Description**: Retrieves detailed information for a specific course taught by the teacher.
- **URL Parameters**:
  - `course_code`: The unique code of the course (e.g., `CS101`).
- **Request**: None
- **Response**:
  ```json
  {
    "course_code": "CS101",
    "course_name": "Introduction to Programming",
    "description": "An introductory course to programming concepts.",
    "semester": "Fall 2024",
    "credits": 3,
    "syllabus_url": "/path/to/syllabus.pdf"
  }
  ```
- **Status Codes**:
  - `200 OK`: Course details retrieved successfully.
  - `401 Unauthorized`: Authentication failed.
  - `403 Forbidden`: Teacher does not teach this course.
  - `404 Not Found`: Course not found.
  - `500 Internal Server Error`: Error retrieving course details.

### 4. Student Management

#### Get Students in a Course
- **Endpoint**: `GET /courses/{course_code}/students`
- **Description**: Retrieves all students enrolled in a specific course
- **URL Parameters**:
  - `course_code`: The unique code of the course (e.g., `CS101`)
- **Response Example**:
  ```json
  [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "course_code": "CS101",
      "roll_no": "CS2021001",
      "name": "John Doe"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "course_code": "CS101",
      "roll_no": "CS2021002",
      "name": "Jane Smith"
    }
  ]
  ```
- **Status Codes**:
  - `200 OK`: Students retrieved successfully
  - `500 Internal Server Error`: Server error

#### Get Enrolled Students in a Course
- **Endpoint**: `GET /courses/{course_code}/students`
- **Description**: Retrieves a list of students enrolled in a specific course.
- **URL Parameters**:
  - `course_code`: The unique code of the course.
- **Request**: None
- **Response**:
  ```json
  [
    {
      "student_id": "STU123",
      "first_name": "Alice",
      "last_name": "Smith",
      "email": "alice.smith@example.com"
    },
    {
      "student_id": "STU456",
      "first_name": "Bob",
      "last_name": "Johnson",
      "email": "bob.johnson@example.com"
    }
  ]
  ```
- **Status Codes**:
  - `200 OK`: Students retrieved successfully.
  - `401 Unauthorized`: Authentication failed.
  - `403 Forbidden`: Teacher cannot view students for this course.
  - `404 Not Found`: Course not found.
  - `500 Internal Server Error`: Error retrieving students.

### 5. Assignment Management

#### Create Assignment
- **Endpoint**: `POST /courses/{course_code}/assignments`
- **Description**: Creates a new assignment for a specific course.
- **URL Parameters**:
  - `course_code`: The unique code of the course.
- **Request Body**:
  ```json
  {
    "title": "Assignment 1: Basic Algorithms",
    "description": "Solve the following algorithmic problems.",
    "due_date": "2024-10-15T23:59:59Z",
    "max_points": 100
  }
  ```
- **Response**:
  ```json
  {
    "message": "Assignment created successfully",
    "assignment_id": "ASN001"
  }
  ```
- **Status Codes**:
  - `201 Created`: Assignment created successfully.
  - `400 Bad Request`: Invalid input data.
  - `401 Unauthorized`: Authentication failed.
  - `403 Forbidden`: Teacher cannot create assignments for this course.
  - `404 Not Found`: Course not found.
  - `500 Internal Server Error`: Error creating assignment.

#### Get Assignments for a Course
- **Endpoint**: `GET /courses/{course_code}/assignments`
- **Description**: Retrieves all assignments for a specific course.
- **URL Parameters**:
  - `course_code`: The unique code of the course.
- **Request**: None
- **Response**:
  ```json
  [
    {
      "assignment_id": "ASN001",
      "title": "Assignment 1: Basic Algorithms",
      "due_date": "2024-10-15T23:59:59Z",
      "max_points": 100
    },
    {
      "assignment_id": "ASN002",
      "title": "Assignment 2: Data Structures Implementation",
      "due_date": "2024-11-05T23:59:59Z",
      "max_points": 150
    }
  ]
  ```
- **Status Codes**:
  - `200 OK`: Assignments retrieved successfully.
  - `401 Unauthorized`: Authentication failed.
  - `403 Forbidden`: Teacher cannot view assignments for this course.
  - `404 Not Found`: Course not found.
  - `500 Internal Server Error`: Error retrieving assignments.

### 6. Grade Management

#### Submit Grades for an Assignment
- **Endpoint**: `POST /assignments/{assignment_id}/grades`
- **Description**: Submits or updates grades for students for a specific assignment.
- **URL Parameters**:
  - `assignment_id`: The unique ID of the assignment.
- **Request Body**:
  ```json
  [
    {
      "student_id": "STU123",
      "score": 85,
      "feedback": "Good effort, some areas need improvement."
    },
    {
      "student_id": "STU456",
      "score": 92,
      "feedback": "Excellent work!"
    }
  ]
  ```
- **Response**:
  ```json
  {
    "message": "Grades submitted successfully for assignment ASN001"
  }
  ```
- **Status Codes**:
  - `200 OK`: Grades submitted/updated successfully.
  - `400 Bad Request`: Invalid input data (e.g., score out of range, invalid student ID).
  - `401 Unauthorized`: Authentication failed.
  - `403 Forbidden`: Teacher cannot grade this assignment.
  - `404 Not Found`: Assignment or student not found.
  - `500 Internal Server Error`: Error submitting grades.

#### Get Grades for an Assignment
- **Endpoint**: `GET /assignments/{assignment_id}/grades`
- **Description**: Retrieves all submitted grades for a specific assignment.
- **URL Parameters**:
  - `assignment_id`: The unique ID of the assignment.
- **Request**: None
- **Response**:
  ```json
  [
    {
      "student_id": "STU123",
      "student_name": "Alice Smith",
      "score": 85,
      "feedback": "Good effort, some areas need improvement.",
      "submitted_at": "2024-10-16T10:00:00Z"
    },
    {
      "student_id": "STU456",
      "student_name": "Bob Johnson",
      "score": 92,
      "feedback": "Excellent work!",
      "submitted_at": "2024-10-16T10:05:00Z"
    }
  ]
  ```
- **Status Codes**:
  - `200 OK`: Grades retrieved successfully.
  - `401 Unauthorized`: Authentication failed.
  - `403 Forbidden`: Teacher cannot view grades for this assignment.
  - `404 Not Found`: Assignment not found.
  - `500 Internal Server Error`: Error retrieving grades.

### 7. Attendance Management

#### Mark Attendance
- **Endpoint**: `POST /attendance`
- **Description**: Records attendance for multiple students in a course
- **Request Body**:
  ```json
  {
    "course_code": "CS101",
    "roll_numbers": ["CS2021001", "CS2021002"]
  }
  ```
- **Response Example**:
  ```json
  [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "student_id": "550e8400-e29b-41d4-a716-446655440000",
      "class_date": "2025-05-11T12:00:00.000Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "student_id": "550e8400-e29b-41d4-a716-446655440001",
      "class_date": "2025-05-11T12:00:00.000Z"
    }
  ]
  ```
- **Status Codes**:
  - `201 Created`: Attendance recorded successfully
  - `400 Bad Request`: Missing required fields or invalid format
  - `500 Internal Server Error`: Server error

#### Get Student Attendance Statistics
- **Endpoint**: `GET /attendance/stats/{student_id}`
- **Description**: Retrieves attendance statistics for a specific student
- **URL Parameters**:
  - `student_id`: The unique ID of the student
- **Query Parameters**:
  - `start_date` (optional): Start date for filtering attendance (ISO format)
  - `end_date` (optional): End date for filtering attendance (ISO format)
- **Response Example**:
  ```json
  {
    "student_id": "550e8400-e29b-41d4-a716-446655440000",
    "student_name": "John Doe",
    "roll_no": "CS2021001",
    "course_code": "CS101",
    "total_classes": 15,
    "attended_classes": 12,
    "attendance_percentage": 80.00,
    "start_date": "2025-01-01T00:00:00.000Z",
    "end_date": "2025-05-11T00:00:00.000Z"
  }
  ```
- **Status Codes**:
  - `200 OK`: Statistics retrieved successfully
  - `404 Not Found`: Student not found
  - `500 Internal Server Error`: Server error

## Error Responses
All API endpoints may return error responses in the following format when an issue occurs:

```json
{
  "error": "A descriptive error message here",
  "details": {
    "field_name": "Specific issue with this field" 
    // Optional: more details about the error
  }
}
```

Common HTTP Status Codes for Errors:
- `400 Bad Request`: The request was malformed or contained invalid parameters.
- `401 Unauthorized`: Authentication is required and has failed or has not yet been provided.
- `403 Forbidden`: The authenticated user does not have permission to access the requested resource.
- `404 Not Found`: The requested resource could not be found.
- `500 Internal Server Error`: An unexpected error occurred on the server.

## Frontend Integration Guide

### Making API Requests
For frontend integration, use the Fetch API or Axios library to make requests to the backend:

```javascript
// Example: Fetching courses for a teacher
async function getTeacherCourses(email) {
  try {
    const response = await fetch(`/api/teacher/courses?email=${encodeURIComponent(email)}`);
    if (!response.ok) {
      throw new Error('Failed to fetch courses');
    }
    return await response.json();
  } catch (error) {
    console.error('Error:', error);
  }
}

// Example: Marking attendance
async function markAttendance(courseCode, rollNumbers) {
  try {
    const response = await fetch('/api/teacher/attendance', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        course_code: courseCode,
        roll_numbers: rollNumbers
      })
    });
    if (!response.ok) {
      throw new Error('Failed to mark attendance');
    }
    return await response.json();
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Data Structures for Frontend
Here are suggested TypeScript interfaces for the frontend:

```typescript
// Course interface
interface Course {
  course_code: string;
  Teacher: string[];
  TA: string[];
  total_classes: number;
}

// Student interface
interface Student {
  id: string;
  course_code: string;
  roll_no: string;
  name: string;
}

// Attendance record interface
interface AttendanceRecord {
  id: string;
  student_id: string;
  class_date: string;
}

// Attendance statistics interface
interface AttendanceStats {
  student_id: string;
  student_name: string;
  roll_no: string;
  course_code: string;
  total_classes: number;
  attended_classes: number;
  attendance_percentage: number;
  start_date: string | null;
  end_date: string | null;
}
```

## Setup and Development

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Environment Variables
Create a `.env` file with the following variables:
- `DATABASE_URL`: PostgreSQL connection string (format: `postgresql://username:password@host:port/database`)

### Installation and Running
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python app.py`

The server will be available at `http://localhost:6969` by default.

### Database Migrations
The project uses Flask-Migrate (Alembic) for database migrations:
- Initialize migrations: `flask db init`
- Create a migration: `flask db migrate -m "description"`
- Apply migrations: `flask db upgrade`

