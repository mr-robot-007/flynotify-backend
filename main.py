from fastapi import FastAPI, HTTPException,Request, Depends
from crud import fetch_all_flights, fetch_flight_by_id,update_flight,add_email_to_passenger_contacts
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import FlightModel,LoginRequest, Flight,PassengerContact,ForgotPasswordModel
import re

from auth import supabase_login,supbase_getUser,supabase_logout,forgot_password


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Add your frontend's origin here
    "*"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    



@app.middleware("http")
async def TokenValidationMiddleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    #  Check if the requested path requires token validation
    if request.url.path not in ["/flights","/logout",re.compile(r"/flights/update/[^/]+$"),re.compile(r"/passengers/update/[^/]+$")]:
        return await call_next(request)

    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return JSONResponse(status_code=401, content={"detail": "Authorization header missing"})
    try:
        user_response = await supbase_getUser(authorization_header)
        request.state.user = user_response  # Store user information in request state
    except Exception:
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

    response = await call_next(request)
    return response



@app.get("/")
async def read_root():
    return {"message": "Welcome to Flight Status API"}





@app.post('/login')
async def login(login_request: LoginRequest):
    username = login_request.username
    password = login_request.password
    return await supabase_login(username, password)

@app.get('/logout')
async def logout():
    return await supabase_logout()

@app.get('/getuser')
async def get_user(request: Request):
    try:
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            raise HTTPException(status_code=401, detail="Authorizationheader missing")
        user_response = await supbase_getUser(authorization_header)
        return user_response
    except Exception as e:
        return e

@app.post('/forgotpassword')
async def forgotpassword(forgotpassword: ForgotPasswordModel):
    return await forgot_password(forgotpassword.email)




@app.get("/flights")
async def get_flights():
    return await fetch_all_flights()

@app.get("/flights/{flight_id}", response_model=FlightModel)
async def get_flight(flight_id: str):
    flight = await fetch_flight_by_id(flight_id)
    if flight:
        return flight
    raise HTTPException(status_code=404, detail="Flight not found")



@app.post('/flights/update/{flight_id}')
async def update_flight_status(flight_id: str, item: Flight):
    return await update_flight(flight_id, item)



@app.post('/passengers/update/{flight_id}')
async def update_passengers(passenger_contact: PassengerContact):
    return await add_email_to_passenger_contacts(passenger_contact.flightId, passenger_contact.email_address)


