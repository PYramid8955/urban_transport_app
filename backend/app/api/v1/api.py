from app.utils import create_map, multigraph_to_cytoscape_json
from app.route_manager import RouteManager

from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import timedelta
from pathlib import Path
import json

from app.core import Security, settings

THIS_FILE = Path(__file__).resolve()
API_DIR = THIS_FILE.parent                  # backend/app/api/v1/
BACKEND_DIR = API_DIR.parents[2]            # backend/
PROJECT_ROOT = BACKEND_DIR.parent           # year_project/
FRONTEND_DIR = PROJECT_ROOT / "frontend"    # year_project/frontend
DATA_DIR = BACKEND_DIR / "data"
PAGE_DIR = FRONTEND_DIR / 'pages'

STATIONS = 100
DENSITY = 1

G = create_map(
        STATIONS, 
        DENSITY,
        DATA_DIR / "map",
        DATA_DIR / "station_names.json",
        min_travel_time=1,    # 1 minute minimum travel time
        max_travel_time=10,   # 10 minutes maximum travel time  
        min_traffic=10,       # 10 passengers minimum
        max_traffic=250       # 250 passengers maximum
    )

rm = RouteManager(G)
rm.gen_routes(verbose=True)

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


@app.get("/")
def index_page(request: Request):
    user = get_user_from_cookie(request)
    if user:
        return RedirectResponse("/admin")

    html = (PAGE_DIR / "index.html").read_text()
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@app.get("/admin")
def admin_page(request: Request):
    user = get_user_from_cookie(request)

    if not user:
        return RedirectResponse(url="/", status_code=302)

    html = (PAGE_DIR / "admin.html").read_text()
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@app.get("/login")
def login_page():
    html = (PAGE_DIR / "login.html").read_text()
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = admin_pwd.get(username)

    if user and security.verify_password(password, user["hashed_password"]):
        token = security.create_access_token(
            {"sub": username},
            expires_delta=timedelta(hours=1)
        )
        SESSIONS[token] = username

        response = RedirectResponse(url="/admin", status_code=302)
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

@app.get("/api/graph")
def get_graph():
    data = multigraph_to_cytoscape_json(rm.Routes[-1])
    return JSONResponse(content = data)

@app.get("/user_path")
def user_path(
    start: str = Query(..., alias="from"),
    end: str = Query(..., alias="to")
):
    try:
        subgraph = rm.shortest_route_path(start, end)
        subgraph['graph'] = multigraph_to_cytoscape_json(subgraph['graph'])
        return JSONResponse(content=subgraph)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
