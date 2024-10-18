import pika
import json
from datetime import datetime

# 1. Nejdríve se pripojim k RabbitMQ
# 2. Por odeslani si inicializuji tunel pro odeslani zpravy



class FileEventSender:

    def template_message(self, message_id, filename, directory, hash_item, change_type, metadata, kontent, size):
        # Ujistěte se, že metadata jsou serializována
        #if isinstance(metadata, dict):
            # Serializace slovníku na JSON
            #metadata = json.dumps(metadata, ensure_ascii=False)

        message = {
            'file_id': message_id,
            'filename': filename,
            'directory': directory,
            'hash_item': hash_item,
            'change_type': change_type,
            'change_time': datetime.now().isoformat(),  # Aktuální čas ve formátu ISO
            'metadata': metadata,  # Nyní je to string ve formátu JSON
            'size': size,
            'content': kontent
        }


        message_body = json.dumps(message, ensure_ascii=False)
        return message_body




    # odesila zpravá do rabbitu
    def send_file_event(self, file_id, change_type, channel, message_body):
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

