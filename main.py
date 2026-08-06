# --- IMPORTS ---
# WHY: We import necessary tools to build the API, interact with the database, and handle data.
# WHERE: These are pulled from your local files (models.py, database.py, schemas.py, auth.py) and external libraries (FastAPI, SQLAlchemy).

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session 
from sqlalchemy import Column, Integer, String

# Local application imports
from database import engine, Base, SessionLocal
import models
from models import Student, User
from schemas import StudentCreate, UserCreate, UserLogin
from auth import hash_password, verify_password, create_access_token


# --- APP INITIALIZATION ---
# WHY: Creates the main application instance that handles web traffic.
# WHERE: This 'app' variable is what an ASGI server (like Uvicorn) runs.
app = FastAPI()

# WHY: This tells SQLAlchemy to look at your models and create the corresponding tables in the database if they don't already exist.
# WHERE: Runs once when the application starts up.
Base.metadata.create_all(bind=engine)


# --- HEALTH CHECK / ROOT ENDPOINT ---
# WHY: A simple endpoint to verify the server is running successfully.
# WHERE: Usually accessed at the root URL (e.g., http://localhost:8000/).
@app.get("/")
async def root():
    return {"message": "first api project"}


# --- DATABASE DEPENDENCY ---
# WHY: Creates a temporary database session for a single request, then automatically closes it when the request is done. This prevents memory leaks and database lockups.
# WHERE: Injected into every endpoint that needs to talk to the database using `Depends(get_db)`.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- STUDENT CRUD OPERATIONS (Create, Read, Update, Delete) ---

# CREATE
# WHY: Accepts JSON data from the client, validates it against `StudentCreate` schema, and saves it to the database as a `Student` model.
# WHERE: Used when a front-end form submits new student registration data.
@app.post("/students")
def create_student(
    student: StudentCreate,          # The incoming validated data
    db: Session = Depends(get_db)    # The active database session
):
    # Map the validated schema data to the database model
    new_student = Student(
        name=student.name,
        email=student.email,
        course=student.course
    )

    db.add(new_student)      # Stage the data
    db.commit()              # Save to the database
    db.refresh(new_student)  # Retrieve the newly generated ID

    return new_student


# READ (ALL)
# WHY: Retrieves a list of all students currently in the database.
# WHERE: Used to display a dashboard or table of enrolled students.
@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students


# READ (SINGLE)
# WHY: Fetches a specific student using their unique ID.
# WHERE: Used when clicking on a specific student's profile to see their details.
@app.get("/students/{id}")
def get_student(id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()

    if not student:
        return {"message": "Student not found"} # Basic error handling

    return student


# UPDATE
# WHY: Finds an existing student by ID and overwrites their data with new input.
# WHERE: Used when an admin edits a student's profile information.
@app.put("/students/{id}")
def update_student(id: int, student: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == id).first()

    if not db_student:
        return {"message": "Student not found"}

    # Overwrite old values with new values
    db_student.name = student.name
    db_student.email = student.email
    db_student.course = student.course

    db.commit()              # Save changes
    db.refresh(db_student)   # Get updated record

    return db_student


# DELETE
# WHY: Finds a student by ID and removes them entirely from the database.
# WHERE: Used when a student drops out or needs to be purged from the system.
@app.delete("/students/{id}")
def delete_student(id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()

    if not student:
        return {"message": "Student not found"}

    db.delete(student) # Remove the record
    db.commit()        # Finalize the deletion

    return {"message": "Student deleted successfully"}


# --- AUTHENTICATION SYSTEM ---

# USER REGISTRATION
# WHY: Creates a new user account. Crucially, it hashes the password before saving it so plaintext passwords are never stored in the database (a major security requirement).
# WHERE: Used on the "Sign Up" page of your application.
@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    hashed_pw = hash_password(user.password) # Secure the password

    new_user = User(
        email=user.email,
        password=hashed_pw
    )
   
    db.add(new_user)
    db.commit()

    return {"message": "User registered"}


# USER LOGIN
# WHY: Verifies a user's identity by checking if the email exists and if the provided password matches the hashed password in the database. If successful, it generates a JWT (JSON Web Token).
# WHERE: Used on the "Log In" page. The returned token is saved by the client (e.g., in a browser cookie or local storage) to access protected routes later.
@app.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    # Step 1: Check if the user exists
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        return {"message": "Invalid credentials"}

    # Step 2: Verify the password matches the hash
    if not verify_password(user.password, db_user.password):
        return {"message": "Invalid credentials"}

    # Step 3: Generate the access token for future authorized requests
    token = create_access_token({"user_id": db_user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }