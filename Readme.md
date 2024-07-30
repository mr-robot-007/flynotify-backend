<h1 align="center" id="title">Flight Notification System Backend</h1>
<h2>🧐 Features</h2>

Here're some of the project's best features:

*   Seamless Flight Search: Users can readily search for flight details using a designated flight ID without login requirements.
*   Secure Admin Login: Admins can log in with proper credentials to unlock a comprehensive suite of administrative features.
*   Flight Information Management: Admins hold the power to update flight details ensuring accuracy and keeping passengers informed.
*   Passenger Management: Admins can effortlessly add new passengers to the system by providing their email addresses.
*   Comprehensive Flight Overview: Admins have a clear view of a list encompassing all flights enabling efficient management.

## Tech
- FASTAPI
- RABBITMQ
- DOCKER
## Prerequisites


- Python 3.11+
- Docker and Docker Compose
## Installation Steps

<p>1. Clone the Repository:</p>

```
git clone https://github.com/mr-robot-007/flynotify-backend
```

<p>2. Navigate to the project directory:</p>

```
cd flynotify-backend
```

<p>3. Create and activate a virtual environment:</p>

```
python -m venv venv
source venv/bin/activate
```

<p>4. Install Dependencies:</p>
```
pip install -r requirements.txt
```
## Configuration

Create a .env file in the root of your project and add the necessary environment variables:
```
SUPABASE_URL=https://fbsswrgjrxhwtjhbhabi.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZic3N3cmdqcnhod3RqaGJoYWJpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjIxMDU2NDgsImV4cCI6MjAzNzY4MTY0OH0.XnuSNC4nnHRT8mpOg9JHSEuKKomr0-Dmo196TrEdqDQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
```
## Running Project Using Docker
```
docker-compose up
```

## OR
## Running the Project without docker
```
- in first terminal
    docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
- second terminal   
    python mail/consume_mail_tasks.py
- in another terminal run
    uvicorn main:app --host 0.0.0.0 --port 8000

npm run dev
```
## Folder Structure
```
flynotify-backend
├── __init__.py
├── __pycache__/
├── auth.py
├── crud.py
├── database.py
├── docker-compose.yml
├── Dockerfile
├── mail/
│   ├── consume_email_tasks.py
│   └── publish_email_tasks.py
├── main.py
├── models.py
├── Readme.md
├── requirements.txt
└── supabaseclient.py
```
## Available Scripts
```
- python mail/consume_mail_tasks.python
- uvicorn main:app --host 0.0.0.0 --port 8000: Starts the FastAPI server
```
## Notes
- Make sure RabbitMQ is running and accessible at the URL specified in the .env file.
- Ensure the SMTP server is configured correctly to send email notifications.
## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.


## License

This project is licensed under the MIT License - see the [MIT](https://choosealicense.com/licenses/mit/) file for details.

