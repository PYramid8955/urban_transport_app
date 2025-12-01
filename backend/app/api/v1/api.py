from app.utils import create_map, get_html_map_raw
from app.route_manager import RouteManager

from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from datetime import timedelta
from pathlib import Path

from app.core import Security, settings

# ----------------------------------------------------------
# PATH FIX
# ----------------------------------------------------------

THIS_FILE = Path(__file__).resolve()
API_DIR = THIS_FILE.parent                  # backend/app/api/v1/
BACKEND_DIR = API_DIR.parents[2]            # backend/
PROJECT_ROOT = BACKEND_DIR.parent           # year_project/
FRONTEND_DIR = PROJECT_ROOT / "frontend"    # year_project/frontend

print("Frontend resolved path:", FRONTEND_DIR)

app = FastAPI(title=settings.APP_NAME)

# Mount static frontend (css/js/html if needed)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

security = Security(secret_key=settings.SECRET_KEY)

admin_pwd = {
    "owner": {
        "username": "owner",
        "hashed_password": security.hash_password("pass12")
    }
}

SESSIONS = {}


def get_user_from_cookie(request: Request):
    token = request.cookies.get("session")
    return SESSIONS.get(token)


# ==========================================================
# ROUTES
# ==========================================================

@app.get("/")
def index_page(request: Request):
    user = get_user_from_cookie(request)

    if user:
        return RedirectResponse(url="/admin", status_code=302)

    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/admin")
def admin_page(request: Request):
    user = get_user_from_cookie(request)

    if not user:
        return RedirectResponse(url="/", status_code=302)

    return FileResponse(FRONTEND_DIR / "admin.html")


@app.get("/login")
def login_page():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = admin_pwd.get(username)

    if user and security.verify_password(password, user["hashed_password"]):
        token = security.create_access_token(
            {"sub": username},
            expires_delta=timedelta(hours=1)
        )
        SESSIONS[token] = username

        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key="session",
            value=token,
            httponly=True,
            max_age=3600,
            samesite="lax"
        )
        return response

    return RedirectResponse(url="/login", status_code=302)


@app.get("/logout")
def logout(request: Request):
    token = request.cookies.get("session")
    SESSIONS.pop(token, None)

    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")
    return response
