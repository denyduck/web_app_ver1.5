import os
import pika
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_models.rabbit_models import Files, FileMetadata, FileChanges, ChangeType
from shared_models import Base
from extract_message_from_json import extract_message_from_json


# ==========================================================================
# Připojení k databazi
# ==========================================================================
class Database:
    def __init__(self):
        DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root_password@db/my_database')
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)


# ==========================================================================
# Třída pro konzumaci zpráv z RabbitMQ
# ==========================================================================
class MessageConsumer:
    def __init__(self, database):
        self.database = database
        self.connection = None
        self.channel = None
        self.file_pdf_path = None
        # navazani spojeni s databazi (pomoci instance tridy dabase)
        session = self.database.Session()
        self.session = session

    def connect(self):
        ''' Připojení k RabbitMQ '''
        credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', 'user'),
            os.getenv('RABBITMQ_PASSWORD', 'password')
        )

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
            port=int(os.getenv('RABBITMQ_PORT', '5672')),
            credentials=credentials
        ))

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='file_events', durable=True)

    def consume_messages(self):
        ''' Registrace callback funkce pro zpracování zpráv '''
        self.channel.basic_consume(
            queue='file_events',
            on_message_callback=self.callback_outcoming,
            auto_ack=True
        )

        print('Čekám na příchozí zprávy. Pro ukončení stiskni CTRL+C')
        self.channel.start_consuming()

    def check_item_db(self, hash):
        ''' Kontrolvani zda se soubor s hash <xyz> nenachazi v db Files ve sloupci hash '''
        existing_file = self.session.query(Files).filter(Files.hash == hash).first()
        print('kontrola pripojeni k datavzi')

        return existing_file is not None

    def callback_outcoming(self, ch, method, properties, body):
        ''' Zpracování příchozí zprávy '''
        # Získání ID a metody zprávy z hlavičky
        mass_head = properties.headers.get('message_id')
        method_type = properties.headers.get('method')
        print(f"Headers - message_id: {mass_head}, method: {method_type}")

        # Dekódování těla zprávy
        message_content = body.decode()
        print(f"Message body decoded: {message_content}")

        # Extrakce dat ze zprávy
        file_id, filename, directory, hash, change_type, metadata, content = extract_message_from_json(message_content)

        self.file_pdf_path = filename

        print(
            f"Extracted message - ID: {file_id}, Filename: {filename}, Directory: {directory}, Hash: {hash}, Type: {change_type}, Metadata: {metadata}, content: {content}")

        ''' Zpracování do databáze podle hlavičky zprávy '''
        session = self.database.Session()  # Otevři novou session

        try:
            if method_type == 'new':
                self.handle_new_message(session, filename, directory, hash, metadata, mass_head, content)
            elif method_type == 'del':
                self.handle_delete_message(session, filename, directory)
            elif method_type == 'edit':
                self.handle_edit_message(session, message_content, filename, hash)

        except Exception as e:
            session.rollback()  # V případě chyby vrátíme změny zpět
            print(f"Chyba při zpracování: {e}")
        finally:
            session.close()  # Zavření session


    def handle_new_message(self, session, filename, directory, hash, metadata, mass_head, content):
        ''' Zpracování nové zprávy '''

        check = self.check_item_db(hash)

        if check:
            print(f"Soubor s hashem {hash} již existuje v databázi. Nová zpráva nebude uložena.")
            return  # Ukončete metodu, pokud existuje

        try:
            message = Files(filename=filename,
                            directory=directory,
                            hash=hash,
                            metadata=metadata,
                            message_id=mass_head,
                            kontent=content)

            session.add(message)
            session.commit()  # Potvrzení změn

            id_db_row = message.id
            print(f"Zprava byla uspesne ulozena s metodou 'new' a prirazenym ID z databeze {id_db_row}.")

            if metadata:  # další informace z metadat do další tabulky
                file_metadata = FileMetadata(
                    file_id=id_db_row,
                    title=metadata.get('title'),
                    keyword=metadata.get('keyword'),
                    description=metadata.get('description'),
                    content_text=metadata.get('content_text')
                )

                session.add(file_metadata)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f'Chyba pri zpracovani souboru {e}')


    def handle_delete_message(self, session, filename, directory):
        ''' Zpracování zprávy pro smazání '''
        existing_message = session.query(Files).filter(Files.filename == filename, Files.directory == directory).first()

        if existing_message:
            change_record = FileChanges(
                file_id=existing_message.id,
                change_type=ChangeType.DELETED,
                old_hash=existing_message.hash,
                new_hash=None,
                old_size=existing_message.size,
                new_size=None
            )

            session.add(change_record)  # Smazání zprávy
            session.commit()  # Potvrzení změn

            session.delete(existing_message)
            session.commit()

            print(f"Zprava: s obsahem '{existing_message}' byla uspesne smazana.")
        else:
            print(f"Žádná zpráva s obsahem '{filename}' nebyla nalezena.")

    def handle_edit_message(self, session, message_content, filename, hash):
        ''' Zpracování zprávy pro editaci '''
        message_to_edit = session.query(Files).filter_by(message_content=message_content).first()
        if message_to_edit:
            change_record = FileChanges(
                file_id=message_to_edit.id,
                filename=filename,
                change_type=ChangeType.MODIFIED,
                old_hash=message_to_edit.hash,
                new_hash=hash,
                old_size=message_to_edit.size,
                new_size=len(message_content),
            )
            session.add(change_record)
            session.commit()  # Potvrzení změn

            # aktualizace záznamu
            message_to_edit.hash = hash
            message_to_edit.size = len(message_content)
            session.commit()  # potvrzení změn

            print(f"Zpráva byla úspěšně aktualizována s novým obsahem.")
        else:
            print(f"Žádná zpráva s obsahem '{message_content}' k editaci nebyla nalezena.")


# ==========================================================================
# Spuštění konzumace zpráv
# ==========================================================================
if __name__ == '__main__':
    database = Database()                   # Inicializace databáze
    consumer = MessageConsumer(database)    # Inicializace konzumenta zpráv
    consumer.connect()                      # Připojení k RabbitMQ
    consumer.consume_messages()             # Spuštění konzumace zpráv

