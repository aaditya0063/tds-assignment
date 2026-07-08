from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI()

# Replace with your TDS login email
EMAIL = "22f2000674@ds.study.iitm.ac.in"

# Your assigned allowed origin
ALLOWED_ORIGIN = "https://dash-zgehzs.example.com"

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# -----------------------------
# Middleware
# -----------------------------
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response


@app.get("/")
def home():
    return {"message": "TDS Assignment API is running"}


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        numbers = [int(x.strip()) for x in values.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="All values must be integers.")

    if not numbers:
        raise HTTPException(status_code=400, detail="Provide at least one integer.")

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers)
    }