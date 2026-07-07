API Documentation - Resume Screening System

Base URL: http://localhost:8000

1. Create Job Description

Creates a new job profile for AI evaluation.

Endpoint: POST /api/v1/jobs
Content-Type: application/x-www-form-urlencoded

Request Parameters

Name

Type

Required

Description

title

string

Yes

Job title (e.g., "Senior Python Developer")

raw_text

string

Yes

Full job description text

required_skills

string

No

Comma-separated list (e.g., "python,fastapi")

preferred_skills

string

No

Comma-separated list (e.g., "docker,aws")

min_experience_years

float

No

Minimum years of experience

Success Response (201 Created)

{
  "status": "success",
  "job_id": 1,
  "title": "Senior Python Developer"
}


2. Screen Resumes

Uploads multiple resume files, parses them, and calculates AI suitability scores against a specific Job ID.

Endpoint: POST /api/v1/resumes/screen/{job_id}
Content-Type: multipart/form-data

Path Parameters

job_id (integer, required): The ID of the target job description.

Request Body

files (Array of Files, required): PDF or DOCX files to be analyzed.

Success Response (200 OK)

{
  "job_id": 1,
  "shortlisted_candidates": [
    {
      "candidate_name": "Jane Doe",
      "score": 85.5,
      "breakdown": {
        "skill_match": 90.0,
        "semantic_match": 82.5,
        "experience_match": 100.0,
        "education_match": 100.0
      },
      "matched_skills": ["python", "fastapi"],
      "missing_skills": ["aws"],
      "preferred_skills": ["docker"],
      "interview_questions": [
        "You have strong Python skills, but can you discuss how you would deploy a FastAPI app on AWS?"
      ]
    }
  ]
}


3. Export to Excel

Converts the shortlisted candidate JSON data into a downloadable .xlsx file.

Endpoint: POST /api/v1/export/excel
Content-Type: application/json

Request Body

{
  "candidates": [
    {
      "candidate_name": "Jane Doe",
      "score": 85.5,
      "email": "jane@example.com",
      "phone": "555-0192"
    }
  ]
}


Success Response (200 OK)

Returns a binary file blob with Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet and triggers a file download named shortlist_report.xlsx.

4. Authentication & User Management

Endpoints for recruiter onboarding, session management, and password recovery.

4.1. User Signup / Registration

Registers a new recruiter account in the system.

Endpoint: POST /api/v1/auth/signup
Content-Type: application/json

Request Body

{
  "name": "Jane HR",
  "email": "jane@company.com",
  "password": "SecurePassword123!"
}


Success Response (201 Created)

{
  "status": "success",
  "message": "Account created successfully. Please log in."
}


4.2. User Login

Authenticates a user and issues an access token.

Endpoint: POST /api/v1/auth/login
Content-Type: application/json

Request Body

{
  "email": "jane@company.com",
  "password": "SecurePassword123!"
}


Success Response (200 OK)

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}


4.3. Forgot Password

Initiates the password recovery process by sending a reset link to the registered email address.

Endpoint: POST /api/v1/auth/forgot-password
Content-Type: application/json

Request Body

{
  "email": "jane@company.com"
}


Success Response (200 OK)

{
  "status": "success",
  "message": "If that email exists in our system, a password reset link has been sent."
}


4.4. Reset Password

Completes the password recovery process using the secure token provided via email.

Endpoint: POST /api/v1/auth/reset-password
Content-Type: application/json

Request Body

{
  "token": "a1b2c3d4e5f6g7h8i9j0",
  "new_password": "NewSecurePassword456!"
}


Success Response (200 OK)

{
  "status": "success",
  "message": "Password successfully updated. You may now log in with your new credentials."
}
