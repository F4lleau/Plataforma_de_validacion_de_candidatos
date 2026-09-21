from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "message": "Junta Electoral API",
        "environment": settings.app_env,
    }


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


# Pydantic errors normally echo rejected inputs; credentials must never be reflected.
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@app.exception_handler(RequestValidationError)
async def sanitized_validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
                for e in exc.errors()
            ]
        },
    )
