from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

class FlightModel(BaseModel):
    flight_id: str
    airline: str
    status: str
    departure_gate: str
    arrival_gate: str
    scheduled_departure: str
    scheduled_arrival: str
    actual_departure: Optional[str] = None
    actual_arrival: Optional[str] = None
    passenger_contacts: Optional[list] = None
    departure: Optional[str] = None

    class Config:
        # This is to help Pydantic parse ObjectId from MongoDB
        json_encoders = {
            ObjectId: str
        }


class LocationModel(BaseModel):
    value:str
    label:str

class LoginRequest(BaseModel):
    username: str
    password: str


class Flight(BaseModel):
    flightId: str
    status: str | None = None
    arrival_gate:str
    departure_gate:str
    scheduled_arrival: str
    scheduled_departure: str
    departure:str

class PassengerContact(BaseModel):
    flightId: str
    email_address: str

class ForgotPasswordModel(BaseModel):
    email:str


class SearchModel(BaseModel):
    keyword:str

class FlightSearchModel(BaseModel):
    loc:str