from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, Base
from routers import vehicles, parking

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Parking Management System",
    version="1.0.0",
    description="Vehicle entry/exit, slot allocation, and billing API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

app.include_router(vehicles.router)
app.include_router(parking.router)

