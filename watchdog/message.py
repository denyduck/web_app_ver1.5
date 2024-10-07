import json
from datetime import datetime


def new_message(message_id, filename, directory, hash, change_type, metadata, kontent):
    # vytvorim slovnik s udajema
    message = {
        'file_id': message_id, #
        'filename': filename,
        'directory': directory,
        'hash': hash,
        'change_type': change_type,
        'change_time': datetime.now().isoformat(),      # Aktuální čas ve formátu ISO
        'metadata': metadata,
        'content': kontent
    }
    message_body = json.dumps(message, ensure_ascii=False)

    return message_body




