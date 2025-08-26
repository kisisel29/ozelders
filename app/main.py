from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from pathlib import Path

from .deps.firebase import initialize_firebase
from .routers import auth, teacher, student, analytics, games

# Initialize Firebase (optional for development)
try:
    initialize_firebase()
except Exception as e:
    print(f"Firebase initialization skipped: {e}")
    # Continue without Firebase for development

app = FastAPI(
    title="Private Math Tutoring Platform",
    description="A comprehensive tutoring platform for grades 5-8",
    version="1.0.0"
)

# Static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(teacher.router, prefix="/api/teacher", tags=["teacher"])
app.include_router(student.router, prefix="/api/student", tags=["student"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(games.router, prefix="/api/games", tags=["games"])


# HTML routes
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/teacher/dashboard", response_class=HTMLResponse)
async def teacher_dashboard(request: Request):
    return templates.TemplateResponse("teacher/dashboard.html", {"request": request})

@app.get("/teacher/classes/{class_id}", response_class=HTMLResponse)
async def teacher_class_detail(request: Request, class_id: str):
    return templates.TemplateResponse("teacher/class_detail.html", {
        "request": request, 
        "class_id": class_id
    })

@app.get("/teacher/assignments/new", response_class=HTMLResponse)
async def teacher_assignment_new(request: Request):
    return templates.TemplateResponse("teacher/assignment_new.html", {"request": request})

@app.get("/teacher/assignments/{assignment_id}", response_class=HTMLResponse)
async def teacher_assignment_detail(request: Request, assignment_id: str):
    return templates.TemplateResponse("teacher/assignment_detail.html", {
        "request": request,
        "assignment_id": assignment_id
    })

@app.get("/teacher/student-tracking", response_class=HTMLResponse)
async def teacher_student_tracking(request: Request):
    return templates.TemplateResponse("teacher/student_tracking.html", {"request": request})

@app.get("/student/home", response_class=HTMLResponse)
async def student_home(request: Request):
    return templates.TemplateResponse("student/home.html", {"request": request})

@app.get("/student/select-teacher", response_class=HTMLResponse)
async def student_select_teacher(request: Request):
    return templates.TemplateResponse("student/select_teacher.html", {"request": request})

@app.get("/student/assignments/{assignment_id}", response_class=HTMLResponse)
async def student_assignment(request: Request, assignment_id: str):
    return templates.TemplateResponse("student/assignment.html", {
        "request": request,
        "assignment_id": assignment_id
    })

@app.get("/games/{game_name}", response_class=HTMLResponse)
async def game_page(request: Request, game_name: str):
    return templates.TemplateResponse(f"games/{game_name}.html", {
        "request": request,
        "game_name": game_name
    })

@app.get("/reports/student/{student_uid}", response_class=HTMLResponse)
async def student_report(request: Request, student_uid: str):
    return templates.TemplateResponse("reports/student.html", {
        "request": request,
        "student_uid": student_uid
    })

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

