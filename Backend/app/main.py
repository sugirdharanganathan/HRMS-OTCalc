from fastapi import FastAPI
from app.database import init_db
from app.routers import employee_router
from app.routers import attendance_router
from fastapi.middleware.cors import CORSMiddleware  # <-- Import this

app = FastAPI(title="HRMS OTC API")

# --- Add this CORS configuration ---
# Define the list of origins that are allowed to make requests
origins = [
    "http://localhost:5173",  # Your React frontend
    "http://127.0.0.1:5173",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allows specific origins
    allow_credentials=True,    # Allows cookies (if you use them)
    allow_methods=["*"],       # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],       # Allows all headers
)
# --- End of CORS configuration ---


app.include_router(employee_router.router, prefix="/api/employees", tags=["employees"])
app.include_router(attendance_router.router, prefix="/api/attendance", tags=["attendance"])


@app.on_event("startup")
def on_startup():
	# create tables if they don't exist
	init_db()


@app.get("/health")
def health():
	return {"status": "ok"}