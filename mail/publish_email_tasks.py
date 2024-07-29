import pika
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))

if rabbitmq_port == '':
    rabbitmq_port = '5672'

def send_email_task(email_data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host,rabbitmq_port,'/',pika.PlainCredentials('guest','guest')))
    channel = connection.channel()
    
    # Declare a queue
    channel.queue_declare(queue='email_tasks')
    
    # Publish the task to the queue
    channel.basic_publish(
        exchange='',
        routing_key='email_tasks',
        body=json.dumps(email_data),
        properties=pika.BasicProperties(
            delivery_mode=2  # Make the message persistent
        )
    )
    print(f"Sent email task: {email_data}")
    connection.close()

# if __name__ == '__main__':
#     email_data = {
#         'to': '2000950100012@coet.in',
#         'subject': 'Test Email',
#         'body': 'This is a test email sent using RabbitMQ.'
#     }
#     send_email_task(email_data)
