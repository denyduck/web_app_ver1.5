import pika

def consume_messages_incoming(message):
    try:
        # Připojení k RabbitMQ serveru s přihlašovacími údaji
        credentials = pika.PlainCredentials('user', 'password')  # Zadejte správné uživatelské jméno a heslo
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=credentials))
        channel = connection.channel()
        # Zajištění, že fronta existuje
        channel.queue_declare(queue='file_events', durable=True)
        # Odeslání zprávy
        channel.basic_publish(
            exchange='',  # Bez výměny
            routing_key='file_events',  # Klíč pro směrování
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Zpráva bude trvalá
            ))

        print(f'Soubor: {message} nahrán do sdílené fronty')  # Debug output
    except Exception as e:
        print(f'Error sending to RabbitMQ: {e}')  # Zpracování chyby
    finally:
        # Uzavření spojení
        if connection:
            connection.close()
