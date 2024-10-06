import pika
from message import new_message



def send_file_event(file_id, change_type, channel, message_body):
    # Odeslání zprávy do RabbitMQ
    channel.basic_publish(
        exchange='',
        routing_key='file_events',
        body=message_body,
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers={
                'message_id': file_id,
                'method': change_type
            }
        )
    )