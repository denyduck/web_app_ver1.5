import json

# prevedeni dat z JSON
def extract_message_from_json(message_content):
    message_data = json.loads(message_content)
    return (
        message_data['file_id'],
        message_data['filename'],
        message_data['directory'],
        message_data['hash_item'],
        message_data['change_type'],
        message_data['metadata'],
        message_data['size'],
        message_data['content']
    )
