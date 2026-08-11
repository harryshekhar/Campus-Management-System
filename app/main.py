from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.test_rbac import router as rbac_test_router
from app.routers.courses import router as courses_router
from app.routers.enrollments import router as enrollments_router
from app.routers.attendance import router as attendance_router
from app.routers.grades import router as grades_router

app = FastAPI(
    title="Campus Management System API",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(rbac_test_router)
app.include_router(courses_router)
app.include_router(enrollments_router)
app.include_router(attendance_router)
app.include_router(grades_router)

@app.get("/")
def root():
    return {
        "message": "Campus Management System API"
    }