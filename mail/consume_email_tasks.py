import pika
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
import time
from dotenv import load_dotenv


# load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

print("Starting consumer script...")  # Initial log to confirm script start
# time.sleep(10)


rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))

if rabbitmq_port == '':
    rabbitmq_port = '5672'

def send_email(to, subject, body):
    # Configure your email server and credentials
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'anujgusain108@gmail.com'
    smtp_password = 'oztjecnllxrhodrj'
    
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        print(f"Email sent to {to}")

def callback(ch, method, properties, body):
    email_data = json.loads(body)
    print(f"Received email task: {email_data}")
    send_email(email_data['to'], email_data['subject'], email_data['body'])
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_email_tasks():
    print(f"Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}")
    attempt = 0
    max_attempts = 10
    while attempt < max_attempts:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port))
            channel = connection.channel()
            
            # Declare the queue
            channel.queue_declare(queue='email_tasks')
            
            # Set up subscription to the queue
            channel.basic_consume(queue='email_tasks', on_message_callback=callback)
            
            print('Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
            break  # Exit the loop if the connection is successful
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(6)
            if attempt == max_attempts:
                print("Max attempts reached. Exiting.")
                break

if __name__ == '__main__':
    consume_email_tasks()
