import json
import os
import pika
from sqlalchemy import create_engine, desc
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


    # ==========================================================================
    def callback_outcoming(self, ch, method, properties, body):
        ''' Zpracování příchozí zprávy '''

        # Získání ID a metody zprávy z hlavičky
        mass_head = properties.headers.get('message_id')
        method_type = properties.headers.get('method')

        print(f"Hlavička - zprava_id: {mass_head}, s metodou: {method_type}")

        # Dekóduj tělo zprávy
        message_content = body.decode()
        print(f"Dekodovaní těla zprávy: {message_content}")

        # Extrahuj data ze zprávy
        try:
            # Nejdříve zkontroluj, zda extract_message_from_json vrací správný počet hodnot a ulož do proměnné
            extracted_data = extract_message_from_json(message_content)
            # Debugging print pro kontrolu extrahovaných dat
            print(f"Extrahovaná data: {extracted_data}")
            # Ujistěte se, že máte správný počet položek
            if len(extracted_data) != 8:    # a pokud je jiný než 8
                raise ValueError(f"Očekávám 8 položek ale dostávám {len(extracted_data)}: {extracted_data}")
            # rozbal data z proměné extracted_data typu JSON
            file_id, filename, directory, hash_item, change_type, metadata, size, content = extracted_data
            # preved mi metadat na slovnik
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata) # nyni jsou prevedeny na platny slovnik
                except json.JSONDecodeError:
                    print("Chyba: Metadata nejsou platný JSON formát.")
                    return

            # zpřístupni mi filename v celé třídě
            self.file_pdf_path = filename
            self.metadata = metadata
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
            return

        # Otevři novou session a pro použití ji ulož do proměnné
        session = self.database.Session()

        try:

            if method_type == "CREATED":
                self.handle_new_message(session, file_id, filename, directory, hash_item, metadata, size, content)

            elif method_type == "DELETED":
                self.edit_item_status(session, filename, directory)
                self.handle_delete_message(session, filename, directory, hash_item, size)

            elif method_type == "MODIFIED": # dodelat metoddu edita
                self.handle_edit_message(session, message_content, filename, hash_item)

            elif method_type == "RENAMED":
                self.handle_rename_message(session, directory)

        except Exception as e:
            session.rollback()  # V případě chyby mi vrat data zpět
            print(f"Chyba při zpracování: {e}")
        finally:
            session.close()  # Zavření session

    # ==========================================================================
    def handle_new_message(self, session, file_id, filename, directory, hash_item, metadata, size, content):
        ''' Zpracování nové zprávy '''

        # Ověřte, že metadata jsou správně naformátována jako slovník:
        if isinstance(metadata, str):
            metadata = json.loads(metadata)  # Převede JSON string na dict
        elif not isinstance(metadata, dict):
            raise ValueError('Metadata musí být string nebo slovník')

        # Nejprve zkontrolujte, zda již existuje soubor s daným hashem
        existing_file = session.query(Files).filter(Files.hash_item == hash_item).first()
        if existing_file:
            print(f"Soubor s hashem {hash_item} již existuje v tabulce Files, nová zpráva nebude uložena.")
            return  # Okamžitě ukončete metodu, pokud již soubor existuje

        # Pokračujte s vytvářením a uložením nové zprávy pouze pokud neexistuje záznam se stejným hashem
        try:
            # Vytvořte novou instanci Items a přidejte ji do relace
            item = Items(
                filename=filename,
                directory=directory,
                change_type=ChangeType.CREATED,
                hash_item=hash_item,
                metadata=metadata,
                kontent=content,
                message_id=file_id,
                size=size
            )
            session.add(item)

            # Vytvořte novou položku v tabulce Files, jelikož zde už víme, že hash není duplicitní
            file = Files(
                filename=filename,
                directory=directory,
                hash_item=hash_item,
                metadata=metadata,
                kontent=content,
                message_id=file_id,
                size=size
            )
            session.add(file)

            # Potvrďte změny v databázi
            session.commit()
            print(f"Zpráva byla úspěšně uložena s ID: {item.id}.")

            # Uložte metadata, pokud existují
            if metadata:
                file_metadata = FileMetadata(
                    file_id=file.id,  # Použití `file.id` po uložení
                    title=metadata.get('title'),
                    keyword=metadata.get('keyword'),
                    description=metadata.get('description'),
                    content_text=metadata.get('content_text')
                )
                session.add(file_metadata)
                session.commit()
                print(f"Metadata byla úspěšně uložena s ID: {file_metadata.id}")

        except Exception as e:
            session.rollback()  # Rollback při chybě
            print(f'Chyba při zpracování souboru: {e}')

    #==========================================================================
    def handle_rename_message(self, session, directory):
        ''' Zpracování zprávy pro přejmenování souboru '''

        # vrat novy nazev ktery predavam z watchdogu do metadat jako new_filename
        data = self.metadata
        filename = self.file_pdf_path # puvodni nazev
        print(f"otestuj cesti s nazvem souboru: {filename}")
        # ted z metadat uloz novy nazev
        new_filename = data.get('new_filename',"Žáadné jméno") #v pripade jej pojmenuj

        # najdi v FILES polozku podle nazvu a cesty
        query_file = session.query(Files).filter(Files.filename == filename, Files.directory == directory).first()
        # najdi v ITEMS polozku podle nazvu a cesty ale jen tu posledni (z duvodu ze v teto tabulce uze byt vice stjnych, pouzij order_by)
        query_file_item = session.query(Items).filter(Items.filename == filename, Items.directory == directory).order_by(desc(Items.created_at)).first()

        # Ověření, zda existuje záznam s `old_filename`
        if query_file and query_file_item:
            print(f"Požadavek na přejmenování z '{filename}' na '{new_filename}' byl zaznamenán.")

            try:
                # Zaznamenání změny názvu do tabulky `FileChanges`
                change_record = FileChanges(
                    filename=query_file.filename,
                    change_type=ChangeType.RENAMED,
                    old_hash=query_file.hash_item,
                    new_hash=query_file.hash_item,  # hash zůstává stejný
                    old_size=query_file.size,
                    new_size=query_file.size  # velikost zůstává stejná
                )
                session.add(change_record)

                # zapis do ITEMS change_type hodnotu RENAMED
                query_file_item.change_type=ChangeType.RENAMED

                # Aktualizace názvu souboru v tabulce `Files`
                query_file.filename = new_filename
                session.commit()  # Potvrzení všech změn

                print(f"Soubor byl úspěšně přejmenován na '{new_filename}'.")
            except Exception as e:
                session.rollback()  # Vrácení změn v případě chyby
                print(f'Chyba při přejmenovávání souboru: {e}')
        else:
            print(f"Soubor s názvem '{new_filename}' nebyl nalezen v databázi.")

    # ==========================================================================
    def edit_item_status(self,session, filename, directory):
        ''' Aktualizace stavu položky na "no_active" pri smazani'''

        # Načtu odpovídající záznam z tabulky Items
        existing_item = session.query(Items).filter(Items.filename == filename, Items.directory == directory).first()

        if existing_item:
            print(f"Našel jsem: {existing_item.filename}, a je {existing_item.is_active}.")

            # Změň stav na "no_active"
            existing_item.is_active = False
            print(f"Položka {existing_item.is_active} je nyní neaktivní a bude smazána")

            # Přidání změněného objektu do session
            session.add(existing_item)
            # Potvrzení změn
            session.commit()

            print(f"Status položky '{existing_item.filename}' byl úspěšně aktualizován na False a položka je smazána.")
        else:
            print(f"Položka {filename} nebyla nalezena v tabulce Items.")

    # ==========================================================================
    def handle_delete_message(self, session, filename, directory, hash_item, size):
        ''' Zpracování zprávy pro smazání souboru '''

        # najdi posledni záznam
        existing_file = session.query(Files).filter(Files.filename == filename, Files.directory == directory).order_by(desc(Files.created_at)).first()

        # a pokud existuje
        if existing_file:
            # ulož hash souboru, abych ho mohl zaznamenat jako "starý hash" ve změnovém záznamu.
            file_hash = existing_file.hash_item
            # uložím původní velikost souboru pro změnový záznam.
            file_size = existing_file.size

            # najdi v ITEMS podle hash radek a
            existing_item = session.query(Items).filter(Items.hash_item == file_hash).order_by(desc(Items.created_at)).all()

            # zmen v ITEMS pro vsechny changetype na DELETED
            for item in existing_item:
                item.change_type = ChangeType.DELETED
                item.is_active = False

            # Vytvořím nový záznam o změně v tabulce FileChanges.
            change_record = FileChanges(
                filename=filename,                  # Původní název souboru, který je smazán.
                change_type=ChangeType.DELETED,     # Typ změny (smazání).
                old_hash=hash_item,                 # Původní hash souboru, který je smazán.
                new_hash=None,                      # Žádný nový hash, protože soubor je smazán.
                old_size=file_size,                 # Původní velikost souboru, který je smazán.
                new_size=None                       # Žádná nová velikost, protože soubor je smazán.
            )
            # přidej záznam o změně do db
            session.add(change_record)
            # Smaž soubor z tabulky Files.
            session.delete(existing_file)

            # Potvrzení všech změn v databázi.
            session.commit()

            # Vypíš potvrzovací zprávu o úspěšném smazání souboru a zaznamenání změny.
            print(f"Soubor s hashi '{file_hash}' v adresáři '{directory}' byl úspěšně smazán a změna byla zaznamenána.")
        else:
            # Pokud soubor nebyl nalezen, vrátím chybovou zprávu.
            print(f"Soubor s názvem '{filename}' v adresáři '{directory}' nebyl nalezen.")
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

