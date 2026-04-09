from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.phase_0_foundation.api_health import router as health_router
from src.phase_0_foundation.core_config import settings
from src.phase_2_retrieval.api_recommendations import router as recommendations_router
from src.phase_4_api_ux.api_api_ux import router as api_ux_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.app_debug,
)

_LOCAL_DEV_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://[::1]:5173",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
    "http://[::1]:4173",
]
_extra_origins = [o.strip() for o in settings.cors_extra_origins.split(",") if o.strip()]
_cors_kw: dict = {
    "allow_origins": _LOCAL_DEV_ORIGINS + _extra_origins,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
_regex = (settings.cors_origin_regex or "").strip()
if _regex:
    _cors_kw["allow_origin_regex"] = _regex

app.add_middleware(CORSMiddleware, **_cors_kw)

app.include_router(health_router)
app.include_router(recommendations_router)
app.include_router(api_ux_router)

app.mount("/ui", StaticFiles(directory="src/phase_4_api_ux/frontend"), name="ui")


@app.get("/")
def ui_home() -> FileResponse:
    return FileResponse("src/phase_4_api_ux/frontend/index.html")
