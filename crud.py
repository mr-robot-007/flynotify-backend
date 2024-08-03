from models import FlightModel,Flight,LocationModel
from re import sub
from database import db
from datetime import datetime
from mail.publish_email_tasks import send_email_task
from fastapi.responses import JSONResponse
import re

from pydantic import BaseModel
# Mock data for flights
flight_data = [
    {
        "flight_id": "6E 2341",
        "airline": "Indigo",
        "status": "On Time",
        "departure_gate": "A12",
        "arrival_gate": "B7",
        "scheduled_departure": "2024-07-26T14:00:00Z",
        "scheduled_arrival": "2024-07-26T18:00:00Z",
        "actual_departure": None,
        "actual_arrival": None,
        "passenger_contacts":[
            {"mode": "email", "value": "anujgusain1083@gmail.com"},
            {"mode": "email", "value": "2000950100012@coet.in"},
        ]
    },
    {
        "flight_id": "6E 2342",
        "airline": "Indigo",
        "status": "Delayed",
        "departure_gate": "C3",
        "arrival_gate": "D4",
        "scheduled_departure": "2024-07-26T16:00:00Z",
        "scheduled_arrival": "2024-07-26T20:00:00Z",
        "actual_departure": None,
        "actual_arrival": None,
        "passenger_contacts":[
            {"mode": "email", "value": "anujgusain1083@gmail.com"},
            {"mode": "email", "value": "2000950100012@coet.in"},
        ]
    },
    {
        "flight_id": "6E 2343",
        "airline": "Indigo",
        "status": "Cancelled",
        "departure_gate": "E2",
        "arrival_gate": "F1",
        "scheduled_departure": "2024-07-26T12:00:00Z",
        "scheduled_arrival": "2024-07-26T16:00:00Z",
        "actual_departure": None,
        "actual_arrival": None,
        "passenger_contacts":[
            {"mode": "email", "value": "anujgusain1083@gmail.com"},
            {"mode": "email", "value": "2000950100012@coet.in"},
        ]
    }
]

# Mock data for notifications
notification_data = [
    {
        "notification_id": "1",
        "flight_id": "6E 2341",
        "message": "Your flight 6E 2341 is on time. Departure gate: A12.",
        "timestamp": "2024-07-26T13:00:00Z",
        "method": "SMS",
        "recipient": "+1234567890"
    },
    {
        "notification_id": "2",
        "flight_id": "6E 2342",
        "message": "Your flight 6E 2342 is delayed. New departure time: 2024-07-26T17:00:00Z. Departure gate: C3.",
        "timestamp": "2024-07-26T15:30:00Z",
        "method": "Email",
        "recipient": "user@example.com"
    },
    {
        "notification_id": "3",
        "flight_id": "6E 2343",
        "message": "Your flight 6E 2343 has been cancelled.",
        "timestamp": "2024-07-26T11:00:00Z",
        "method": "App",
        "recipient": "user_app_id_12345"
    }
]




# Use a regex to insert a space between letters and numbers to format the flight ID
def format_flight_id(flight_id: str) -> str:
    return sub(r"([a-zA-Z])(\d)", r"\1 \2", flight_id.upper())


async def fetch_all_flights():
    flights = []
    data = db.flights.find()
    for flight in data:
        flight['id'] = flight['_id']
        flights.append(FlightModel(**flight))
    return flights

async def fetch_flight_by_id(flight_id: str):
    x = format_flight_id(flight_id)
    flight = db.flights.find_one({"flight_id": x})
    if flight is not None:
        flight['id'] = str(flight['_id'])
        return FlightModel(**flight)
    return None



async def add_email_to_passenger_contacts(flight_id, new_email):
    collection = db['flights']
    # Find the document with the given flight_id
    document = collection.find_one({"flight_id": flight_id})
    
    if not document:
        print("Flight not found.")
        return

    # Check if the email already exists in the passenger_contacts array
    for contact in document["passenger_contacts"]:
        if contact["value"] == new_email:
            print("Email already exists.")
            return JSONResponse(status_code=200, content={"detail": "Email Already Exists"})
    
    # Add the new email to the passenger_contacts array
    result = collection.update_one(
        {"_id": document["_id"]},
        {"$push": {"passenger_contacts": {"mode": "email", "value": new_email}}}
    )
    if result.modified_count > 0:
        print(f"Successfully added  new passenger for flightId: {flight_id}.")

        return JSONResponse(status_code=200, content={"detail": "New passenger added successfully"})
    else:
        print("No changes made to the document.")
        return JSONResponse(status_code=201, content={"detail": "Nothing to update."})


async def update_flight(flight_id: str, data:Flight):
    print('hii')
    print(data.scheduled_arrival)
    collection = db['flights']
    flight_data = {
        'status': data.status,
        'arrival_gate': data.arrival_gate,
        'departure_gate': data.departure_gate,
        'scheduled_arrival' : data.scheduled_arrival+':00Z',
        'scheduled_departure' : data.scheduled_departure+':00Z',
    }
    result = collection.update_one(
        {'flight_id': data.flightId},  # Filter document to update by flightId
        {'$set': flight_data},  # Set the new data
        # upsert=True  # Create the document if it does not exist
    )
    print("result : ",result)
    if result.modified_count > 0:
        print(f"Successfully updated the flight data for flightId: {data.flightId}")

        await push_notification(data.flightId,data)
        return JSONResponse(status_code=201, content={"detail": "Flight data updated successfully"})
    else:
        print("No changes made to the document.")
        return JSONResponse(status_code=201, content={"detail": "Nothing to update."})


async def push_notification(flightId,flight):
    collection = db['flights'];
    result = collection.find_one({"flight_id": flightId});
    reciepents = [];
    if(result is not None):
        for contact in result['passenger_contacts']:
            reciepents.append(contact['value'])

    email_data = {
        'subject': 'Flight Update',
    }
    if(flight.status == 'Cancelled'):
        email_data['body'] = (
            f"Dear Passenger,\n\n"
            f"We would like to inform you that your flight {flightId} is currently {flight.status}.\n\n"
            f"Thank you for flying with us.\n\n"
            f"Best regards,\n"
            f"Your Airline Team"
        )
    else :
        email_data['body'] = (
            f"Dear Passenger,\n\n"
            f"We wanted to inform that your flight {flightId} is {flight.status}.\n\n"
            f"Flight Details:\n"
            f"Flight ID: {flightId}\n"
            f"Departure Gate: {flight.departure_gate}\n"
            f"Arrival Gate: {flight.arrival_gate}\n"
            f"Scheduled Departure: {flight.scheduled_departure}\n"
            f"Scheduled Arrival: {flight.scheduled_arrival}\n\n"
            f"Please ensure you arrive at the departure gate on time. We apologize for any inconvenience caused and appreciate your understanding.\n\n"
            f"Thank you for flying with us.\n\n"
            f"Best regards,\n"
            f"Indigo Airline Team"
        )
    
    for email in reciepents:
        email_data['to'] = email
        send_email_task(email_data)
    


def insert_flights():
    collection = db['flights']
    for flight in flight_data:
        collection.insert_one(flight)

options = [
  { "value": "Delhi", "label": "Delhi" },
  { "value": "Dehradun", "label": "Dehradun" },
  { "value": "New Delhi", "label": "New Delhi" },
  { "value": "Chandigarh", "label": "Chandigarh" },
  { "value": "Gujrat", "label": "Gujrat" },
  { "value": "Gwalior", "label": "Gwalior" },
  { "value": "Jaipur", "label": "Jaipur" },
  { "value": "Kota", "label": "Kota" },
  { "value": "Lucknow", "label": "Lucknow" },
  { "value": "Mumbai", "label": "Mumbai" },
  { "value": "Pune", "label": "Pune" },
  { "value": "Rajasthan", "label": "Rajasthan" },
  { "value": "Surat", "label": "Surat" },
  { "value": "Udaipur", "label": "Udaipur" },
  { "value": "Varanasi", "label": "Varanasi" },
  { "value": "Vishakhapatnam", "label": "Vishakhapatnam" }
]

async def insert_locations():
    collection = db['locations']
    for location in options:
        collection.insert_one(location)
    return {"status": "success"}


async def get_locations(keyword):
    print(keyword)
    collection = db['locations']
    regex = re.compile(f".*{keyword}.*", re.IGNORECASE)
    cursor = collection.find({"value": {"$regex": regex}},)
    seen = set()
    locations = []
    for data in cursor:
        location = LocationModel(**data)
        if location.value not in seen:
            seen.add(location.value)
            locations.append(location)
    print(locations)
    return locations


async def search_flights_by_keyword(loc):
    collection = db['flights']
    flights = []
    regex = re.compile(f".*{loc}.*", re.IGNORECASE)
    cursor = collection.find({"departure": {"$regex": regex}},)
    seen = set()
    for data in cursor:
        flight = FlightModel(**data)
        if data['flight_id'] not in seen:
            seen.add(data['flight_id'])
            flights.append(flight)
    return flights