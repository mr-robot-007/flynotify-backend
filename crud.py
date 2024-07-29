from models import FlightModel, NotificationModel,Item
from re import sub
from database import db
from datetime import datetime
from mail.publish_email_tasks import send_email_task
from fastapi.responses import JSONResponse

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

# uri = "mongodb+srv://admin-anuj:Cqm3TkJWk65a0PKA@cluster0.tfrcerl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)



# db = client['indigo_db']



def format_flight_id(flight_id: str) -> str:
    # Use a regex to insert a space between letters and numbers
    return sub(r"([a-zA-Z])(\d)", r"\1 \2", flight_id.upper())

async def fetch_all_flights():
    flights = []
    data = db.flights.find()
    for flight in data:
        flight['id'] = flight['_id']
        flights.append(FlightModel(**flight))
    return flights
    # return [FlightModel(**flight) for flight in flight_data]

async def fetch_flight_by_id(flight_id: str):
    x = format_flight_id(flight_id)
    flight = db.flights.find_one({"flight_id": x})
    if flight is not None:
        flight['id'] = str(flight['_id'])
        return FlightModel(**flight)
    return None



async def fetch_all_notifications():
    notifications = []
    data = db.notifications.find()
    
    for notification in data:
        print(notification)
        notification['id'] = notification['_id']
        notifications.append(NotificationModel(**notification))
    return notifications

async def fetch_notifications_by_flight_id(flight_id: str):
    notifications = [notification for notification in notification_data if notification["flight_id"] == flight_id]
    return [NotificationModel(**notification) for notification in notifications] if notifications else []



async def update_flight(flight_id: str, data:Item):
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
    