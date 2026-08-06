from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

# 'Base' is the declarative base class from SQLAlchemy. 
# WHERE: Imported from your local database configuration file (e.g., database.py).
# WHY: All models inherit from this so SQLAlchemy knows they represent database tables.
from database import Base

class User(Base):
    # WHY: Specifies the exact name of the table in the SQL database.
    __tablename__ = "users"

    # WHERE: Used as the unique identifier for each row in the 'users' table.
    # WHY: primary_key=True makes it the PK, index=True speeds up queries searching by ID.
    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)
    # WHY: unique=True ensures no two users can register with the same email.
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # WHY: Determines authorization levels (e.g., student, admin, teacher). Defaults to "student".
    role = Column(String, default="student")

    # WHERE/WHY: Automatically records exactly when a user registers. 
    # Used for analytics, auditing, or sorting users by registration date.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # WHERE/WHY: Automatically updates the timestamp whenever the user's record is modified 
    # (e.g., if they change their password).
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # WHERE: Used in your Python code (not in the database itself).
    # WHY: Creates a link between the User and Student objects. If you have a user object `u`, 
    # you can access their student profile via `u.students` without writing a SQL JOIN query.
    students = relationship(
        "Student",
        back_populates="user"
    )


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)

    # WHY: Allows you to easily fetch all students in a specific department 
    # (e.g., `computer_science_dept.students`).
    students = relationship(
        "Student",
        back_populates="department"
    )


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    course = Column(String)

    # WHERE: Represents a physical column in the 'students' table.
    # WHY: ForeignKey tells the database that this column links directly to the 'id' column in the 'users' table. 
    # This enforces relational integrity (you can't link to a user that doesn't exist).
    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    # WHY: Links the student to a specific department. nullable=True means a student 
    # can exist without being assigned to a department yet.
    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=True
    )

    # WHERE: Used in your Python code to navigate back to the parent objects.
    # WHY: 'back_populates' syncs the relationship in memory. If you update `student.department`, 
    # SQLAlchemy knows to also update `department.students` automatically.
    user = relationship(
        "User",
        back_populates="students"
    )

    department = relationship(
        "Department",
        back_populates="students"
    )