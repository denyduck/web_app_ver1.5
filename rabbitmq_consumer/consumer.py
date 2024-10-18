import json
import os
import pika
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_models.rabbit_models import Files, FileMetadata, FileChanges, ChangeType, Items
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

    # ==========================================================================
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

    # ==========================================================================
    def consume_messages(self):
        ''' Registrace callback funkce pro zpracování zpráv '''
        self.channel.basic_consume(
            queue='file_events',
            on_message_callback=self.callback_outcoming,
            auto_ack=True
        )

        print('Čekám na příchozí zprávy. Pro ukončení stiskni CTRL+C')
        self.channel.start_consuming()

    # ==========================================================================
    def check_item_db(self, hash_item):
        ''' Zkontroluje, zda položka s daným hashem existuje v databázi. '''

        try:
            # Vyhledáme existující položku podle jejího hashe
            existing_file = self.session.query(Items).filter(Items.hash_item == hash_item).first()

            # Debugovací výstup pro sledování, co bylo hledáno
            print(f'Hledá se položka s hashem: {hash_item}')

            # Zjistíme, zda položka existuje
            if existing_file:
                print(f'Položka s hashem {hash_item} byla nalezena v databázi.')
            else:
                print(f'Položka s hashem {hash_item} nebyla nalezena v databázi.')

            # Vrátíme True, pokud položka existuje, jinak False
            return existing_file is not None

        except Exception as e:
            # Ošetření výjimky a výstup chybové zprávy pro debug
            print(f'Chyba při kontrole databáze: {e}')
            return False

    # ==========================================================================
    def callback_outcoming(self, ch, method, properties, body):
        ''' Zpracování příchozí zprávy '''
        # Získání ID a metody zprávy z hlavičky
        mass_head = properties.headers.get('message_id')
        method_type = properties.headers.get('method')

        print(f"Hlavička - zprava_id: {mass_head}, s metodou: {method_type}")

        # Dekódování těla zprávy
        message_content = body.decode()
        print(f"Dekodovaní těla zprávy: {message_content}")

        # Extrakce dat ze zprávy
        try:
            # Zde zkontrolujte, zda extract_message_from_json vrací správný počet hodnot
            extracted_data = extract_message_from_json(message_content)

            # Debugging print pro kontrolu extrahovaných dat
            print(f"Extrahovaná data: {extracted_data}")

            # Ujistěte se, že máte správný počet položek
            if len(extracted_data) != 8:
                raise ValueError(f"Expected 8 items but got {len(extracted_data)}: {extracted_data}")

            file_id, filename, directory, hash_item, change_type, metadata, size, content = extracted_data


            self.file_pdf_path = filename

            # Výpis jednotlivých položek pro debug
            print(f"Extracted message - ID: {file_id}")
            print(f"Filename: {filename}")
            print(f"Directory: {directory}")
            print(f"Hash: {hash_item}")
            print(f"Type: {change_type}")
            print(f"Metadata: {metadata}")
            print(f"Size: {size}")
            print(f"Content: {content}")

        except Exception as e:
            print(f"Chyba při extrakci dat: {e}")
            return  # Můžete se rozhodnout, zda chcete pokračovat nebo ne

        ''' Zpracování do databáze podle hlavičky zprávy '''
        session = self.database.Session()  # Otevři novou session

        try:
            if method_type == 'new':
                self.handle_new_message(session, file_id, filename, directory, hash_item, metadata, size, content)

            elif method_type == 'del':
                self.handle_delete_message(session, filename, directory, hash_item, size)
            elif method_type == 'edit':
                self.handle_edit_message(session, message_content, filename, hash_item)

        except Exception as e:
            session.rollback()  # V případě chyby vrátíme změny zpět
            print(f"Chyba při zpracování: {e}")
        finally:
            session.close()  # Zavření session

    # ==========================================================================
    def handle_new_message(self, session, file_id, filename, directory, hash_item, metadata, size, content):
        ''' Zpracování nové zprávy '''
        # zkontroluj co je v adresari pri zapnuti watchdoga
        check = self.check_item_db(hash_item)
        print()
        if check:
            print(f"Soubor s hashem {hash_item} již existuje v databázi. Nová zpráva nebude uložena.")
            return  # Ukončete metodu, pokud existuje

        try:
            if isinstance(metadata, str):
                metadata = json.loads(metadata) # prevede json stringu na dic
            elif not isinstance(metadata,dict):
                raise ValueError('Metada musi byt string nebo slovnik')

            item = Items(filename=filename,
                            directory=directory,
                            hash_item=hash_item,
                            metadata=metadata,
                            kontent=content,
                            message_id=file_id,
                            size=size
                            )
            session.add(item)
            session.commit()  # Potvrzení změn


            file = Files(filename=filename,
                            directory=directory,
                            hash_item=hash_item,
                            metadata=metadata,
                            kontent=content,
                            message_id=file_id,
                            size=size
                            )
            session.add(item)
            session.add(file)
            session.commit()  # Potvrzení změn



            id_db_row = item.id
            print(f"Zprava byla uspesne ulozena s metodou 'new' a prirazenym ID z databeze {id_db_row}.")
           # Debugging: zkontroluj typ a obsah metadat
            print(f"Typ metadat: {type(metadata)}")
            print(f"Obsah metadat: {metadata}")

            existing_file = session.query(Files).filter(Files.hash_item == hash_item).first()
            if not existing_file:
                print(f'Soubor s hashem {hash_item} neexistuje. Metadata nebudou uložena')


            #POZOR NA DATOVY TYP!! prijima pouze slovnik!
            if metadata:  # další informace z metadat do další tabulky
                file_metadata = FileMetadata(
                    file_id=existing_file.id,
                    title=metadata.get('title'),
                    keyword=metadata.get('keyword'),
                    description=metadata.get('description'),
                    content_text=metadata.get('content_text')
                )

                session.add(file_metadata)
                session.commit()
                print(f"Metadata byla úspěšně uložena s ID: {file_metadata.id}")
        except Exception as e:
            session.rollback()
            print(f'Chyba pri zpracovani souboru v def handle_new_message {e}')

    # ==========================================================================
    def handle_delete_message(self, session, filename, directory, hash_item, size):
        ''' Zpracování zprávy pro smazání souboru '''

        # Vyhledáme existující soubor podle filename a directory,
        # protože smazaný soubor nemůže mít vypočtený hash.
        existing_file = session.query(Files).filter(Files.filename == filename, Files.directory == directory).first()

        # Pokud soubor existuje v databázi
        if existing_file:
            # Uložíme původní hash souboru, abychom ho mohli zaznamenat jako "starý hash" ve změnovém záznamu.
            file_hash = existing_file.hash_item
            # Uložíme původní velikost souboru pro změnový záznam.
            file_size = existing_file.size
            # Vytvoříme nový záznam o změně v tabulce FileChanges.
            change_record = FileChanges(
                filename=filename,  # Původní název souboru, který je smazán.
                change_type=ChangeType.DELETED,  # Typ změny (smazání).
                old_hash=file_hash,  # Původní hash souboru, který je smazán.
                new_hash=None,  # Žádný nový hash, protože soubor je smazán.
                old_size=file_size,  # Původní velikost souboru, který je smazán.
                new_size=None  # Žádná nová velikost, protože soubor je smazán.
            )

            # Přidáme záznam o změně do databáze.
            session.add(change_record)

            # Poté, co zaznamenáme změnu, můžeme bezpečně smazat soubor z tabulky Files.
            session.delete(existing_file)

            # Potvrzení změn v databázi, které zahrnují přidání záznamu do FileChanges a smazání souboru.
            session.commit()

            # Vypíšeme potvrzovací zprávu o úspěšném smazání souboru a zaznamenání změny.
            print(
                f"Soubor s hashi '{file_hash}' v adresáři '{directory}' byl úspěšně smazán a změna byla zaznamenána.")
        else:
            # Pokud soubor nebyl nalezen, vrátíme chybovou zprávu.
            print(f"Soubor s hash_item '{filename}' v adresáři '{directory}' nebyl nalezen.")

    #==========================================================================
    def handle_edit_message(self, session, message_content, filename, hash_item):
        ''' Zpracování zprávy pro editaci '''
        message_to_edit = session.query(Files).filter_by(message_content=message_content).first()
        if message_to_edit:
            change_record = FileChanges(
                #file_id=message_to_edit.id,
                filename=filename,
                change_type=ChangeType.MODIFIED,
                old_hash=message_to_edit.hash_item,
                new_hash=hash_item,
                old_size=message_to_edit.size,
                new_size=len(message_content),
            )
            session.add(change_record)
            session.commit()  # Potvrzení změn

            # aktualizace záznamu
            message_to_edit.hash = hash_item
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

