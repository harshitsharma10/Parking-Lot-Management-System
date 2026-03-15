from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import UserRoutes, ParkingRoutes
import models.user_model
import models.parking_slot_model
import models.parking_session_model
from database import engine, Base

app = FastAPI(title="Parking Lot Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,                   
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UserRoutes.router)
app.include_router(ParkingRoutes.router)

Base.metadata.create_all(bind=engine)