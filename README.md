# Campus Management System

A modern campus management application designed to simplify academic administration through a user-friendly interface, structured database operations, and REST API integration.

The project uses **React, TypeScript, TanStack Start, and Tailwind CSS** for the frontend, with **FastAPI, PostgreSQL, and SQLAlchemy** for backend services and data management.

## Features

- **Student Management:** Manage and retrieve student records.
- **Department Management:** Organize departments and related academic information.
- **Course Management:** Maintain course information and student enrollments.
- **Teacher Management:** Organize teacher records and related information.
- **Database Integration:** Store and retrieve data using PostgreSQL and SQLAlchemy.
- **Pagination:** Display records in manageable pages for more efficient data browsing.
- **Input Validation:** Validate submitted data to help prevent invalid records.
- **Authentication and Authorization:** Support login and role-based access control.
- **Responsive GUI:** Provide a clean, organized interface for easier navigation.
- **API Documentation:** Explore and test backend endpoints using FastAPI's Swagger UI.
- **Containerization:** Use Docker and Docker Compose to simplify application setup and deployment.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, TanStack Start |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Database Migrations | Alembic |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |

## Getting Started

### Prerequisites

Install the following tools:

- Node.js and npm
- Python
- PostgreSQL, or Docker
- Git

### Frontend Setup

Clone the repository and install the dependencies:

```bash
git clone <your-repository-url>
cd <repository-name>
npm install
npm run dev
```

Open the local URL shown in the terminal to access the application.

### Backend Setup

Navigate to your backend project directory and configure the Python environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure the required environment variables, including `DATABASE_URL`, according to your backend configuration.

Start the FastAPI server using the appropriate application module:

```bash
uvicorn app.main:app --reload
```

The API documentation is generally available at:

```text
http://127.0.0.1:8000/docs
```

Make sure the database is running and the frontend is configured to connect to the correct API URL.

## Project Objectives

- Simplify the management of student and academic records.
- Improve data consistency through structured database operations and validation.
- Make record retrieval more convenient through pagination and organized interfaces.
- Improve maintainability through modular application code and database migrations.
- Support secure access to protected operations through authentication and role-based permissions.

## Future Enhancements

- Advanced search, filtering, and sorting.
- Attendance and academic performance tracking.
- Reporting and analytics dashboards.
- Notifications and administrative workflows.
- Further performance and security improvements.

## Contributing

Contributions and suggestions are welcome. Fork the repository, create a feature branch, implement your changes, and submit a pull request.

## License

Add an appropriate license before distributing the project publicly.
