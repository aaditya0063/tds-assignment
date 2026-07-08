from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
import uuid
import time
import os 

app = FastAPI()

# -----------------------------
# Configuration
# -----------------------------
EMAIL = "22f2000674@ds.study.iitm.ac.in"

ALLOWED_ORIGIN = "https://dash-zgehzs.example.com"

ISSUER = "https://idp.exam.local"

AUDIENCE = "tds-k33y8a3g.apps.exam.local"

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

# -----------------------------
# Request Model
# -----------------------------
class TokenRequest(BaseModel):
    token: str

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
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

# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {"message": "TDS Assignment API is running"}

# -----------------------------
# Question 1
# -----------------------------
@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        numbers = [int(x.strip()) for x in values.split(",") if x.strip()]
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"error": "All values must be integers"},
        )

    if len(numbers) == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "No values provided"},
        )

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }

# -----------------------------
# Question 2
# -----------------------------
@app.post("/verify")
def verify(data: TokenRequest):

    try:
        payload = jwt.decode(
            data.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }

    except InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={
                "valid": False
            },
        )
    
# -----------------------------
# Question 3
# -----------------------------
@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    # -----------------------
    # Defaults
    # -----------------------
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000",
    }

    # -----------------------
    # YAML
    # -----------------------
    config.update({
        "workers": 14,
        "debug": True,
    })

    # -----------------------
    # .env
    # -----------------------
    config["workers"] = 15
    config["debug"] = True
    config["log_level"] = "info"

    # -----------------------
    # OS Environment
    # -----------------------
    config["port"] = int(os.getenv("APP_PORT", 8287))
    config["workers"] = int(os.getenv("APP_WORKERS", 11))

    debug = os.getenv("APP_DEBUG", "false").lower()
    config["debug"] = debug in ("true", "1", "yes", "on")

    # -----------------------
    # CLI Overrides
    # -----------------------
    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key in ("port", "workers"):
            config[key] = int(value)

        elif key == "debug":
            config[key] = value.lower() in (
                "true",
                "1",
                "yes",
                "on",
            )

        else:
            config[key] = value

    # -----------------------
    # Mask Secret
    # -----------------------
    config["api_key"] = "****"

    return config