#==========================================================================
# Importy
#==========================================================================

# Importuje moduly pro manipulaci se soubory a čas
import os
import time  # Modul pro čekání během běhu programu

# Importuje moduly pro práci s RabbitMQ
import pika
import json
# Import pro získání správného adresáře (lokální nebo Docker)
from config_watchdog import docker_or_local

# Import pro zpracování událostí systému souborů
from watchdog.events import FileSystemEventHandler, FileMovedEvent          # Zpracovává události (např. změna souborů)
from watchdog.observers.polling import PollingObserver      # Sledování změn souborového systému

# Importuje moduly pro generování unikátních ID
import uuid

from shared_models.rabbit_models import ChangeType

from message_handler import FileEventSender


# Import pro manipulaci s textem a obrázky PDF
import re
from pdf2image import convert_from_path         # Převod PDF na obrázky
import pytesseract                              # OCR pro převod textu z obrázků
from pdfminer.high_level import extract_text    # Extrakce textu z PDF

# Vytvoření unikátního ID pro zprávu
message_id = str(uuid.uuid4())

# Určení adresáře, který se bude sledovat
directory_dog = docker_or_local()   # Vrací cestu k adresáři podle prostředí (Docker nebo lokální
# Debug výstup



print("Načtení skriptu ..")
print(directory_dog)



#==========================================================================
# Sledovač
#==========================================================================
class Watcher:

    def __init__(self):
        """Konstruktor třídy Watcher. Vytvoří instanci Observer."""
        #self.observer = Observer()
        self.directory_dog = directory_dog
        self.observer = PollingObserver()

    # ==========================================================================
    def run(self):
        """Inicializuje sledování a spouští sledování změn v adresáři."""
        event_handler = Handler()  # Vytvoří instanci handleru
        event_handler.check_directory()
        event_handler.simulate_existing_files()

        try:
            self.observer.schedule(event_handler, self.directory_dog, recursive=True)
            print(f'Sledování adresáře: {self.directory_dog}') # Debug output
            self.observer.start() # Spustí sledování adresáře

        except FileNotFoundError as e:
            print(f'Chyba: Adresář {self.directory_dog} nebyl nalezen',)
            return

        except PermissionError as e:
            print(f'Chyba: Nedostatečná opravnění pro přístup k adresáři {self.directory_dog}.')
            return

        except Exception as e:
            print(f'Nastala neočekávaná chyba: {e}')
            return

        try:
            while True:
                time.sleep(5)  # Program běží
                print("Skript běží...")
        except KeyboardInterrupt:
            self.observer.stop()  # Ošetření výjimky
            print('Sledování zastaveno!')
        except Exception as e:
            print(f'Nastala neočekávaná chyba při běhu skriptu: {e}')
        finally:
            self.observer.join()  # Čeká, dokud není sledování ukončeno


# ==========================================================================
# PDF PROCESOR
# ==========================================================================

class Pdf_processor():

    def __init__(self):
        self.text_from_images_pdf = None
        self.text_from_text_pdf = None

    # ==========================================================================
    def text_pdf(self, file_path):
       try:
            # Extrahuje text z adresáře uloženého v self.directory_dog
            print(f'Debu text_pdf vyhodnoceni souboru {file_path}')
            text = extract_text(file_path)
            if text and text.strip():
                return text         # pdf obsahuje text
            else:
                return None         # Pdf pradedpodbne neosbahuje text

       except Exception as e:
           print(f"Chyba při extrakci textu: {e}")
           return None

    def ocr_pdf(self, file_path):
        # Převod PDF na obrázky
        print(f'provadim debug na ocr_pdf {file_path}')
        images = convert_from_path(file_path)

        text = ''
        for img in images:
            # Provádění OCR na každém obrázku
            text += pytesseract.image_to_string(img) + '\n'
        print(f'toto je debug ocr_pdf{text}')
        return text

    def proces_pdf(self, file_path):
        # Zkontrolujeme, zda PDF obsahuje text
        extracted_text = self.text_pdf(file_path)


        if extracted_text is not None:
            # Vyčistit extrahovaný text
            cleaned_text = re.sub(r'[^a-zA-Z0-9\s,.;:!?"\'()\-–—]', '', extracted_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Odstranění nadbytečných mezer

            self.text_from_text_pdf = cleaned_text  # Uložení vyčištěného textu jako atribut instance

            return cleaned_text  # Vraťte vyčištěný text
        else:
            # Pokud text neexistuje, provést OCR
            extracted_images = self.ocr_pdf(file_path)
            self.text_from_images_pdf = extracted_images
            return self.text_from_images_pdf # Vraťte text získaný z OCR


#==========================================================================
# Pripojeni k RabitMq
#==========================================================================

class RabbitMQConnection:
    def __init__(self):
        """Inicializuje připojení k RabbitMQ s údaji z prostředí."""
        self.credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', 'user'),
            os.getenv('RABBITMQ_PASSWORD', 'password')
        )
        self.host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.connection = None
        self.channel = None
        self.message_id = str(uuid.uuid4())
        # instance FileEventSender
        self.file_event_sender = FileEventSender()
        self.extract_kontent = None  # nejdrive se bude nastavavovat atribut, proto pocatecni None
        self.filename = None

        self.connect()

    # ==========================================================================
    def connect(self):
        """Vytvoří připojení a otevře kanál k RabbitMQ."""
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=self.credentials))
            self.channel = self.connection.channel()
            print("Připojení k RabbitMQ bylo úspěšné.")
            self.channel.queue_declare(queue='file_events', durable=True)
        except Exception as e:
            print(f'Chyba při připojení k RabbitMQ: {e}')
            self.close()

    # ==========================================================================

    def send_message(self, file_id, filename, directory, hash_item, change_type, metadata, kontent, size):

        """Odešle zprávu o změně souboru do fronty RabbitMQ."""
        if self.channel is None or not self.channel.is_open:
            print("Připojení není otevřené, pokusím se znovu připojit.")
            self.connect()

        try:
            # pokud metada je slovnik, prevest ho na JSON (rabbit ocekava retezec) ne stringy a slovniky
            if isinstance(metadata, dict):
                metadata = json.dumps(metadata, ensure_ascii=False)
            # Vytvoř zprávu
            message_body = self.file_event_sender.template_message(
                file_id,
                filename,
                directory,
                hash_item,
                change_type,
                metadata,
                kontent,
                size
            )

            print(f"Zpráva vytvořena: {message_body}")

            # Odeslání zprávy
            self.file_event_sender.send_file_event(
                file_id,
                change_type,
                self.channel,
                message_body
            )

            print(f"Zpráva odeslána pro soubor: {filename}")
        except Exception as e:
            print(f'Chyba při odesílání zprávy: {e}')
        finally:
            self.close()

    # ==========================================================================
    def get_pdf_name(self):
        return self.filename


    # ==========================================================================
    def close(self):
        """Uzavře připojení k RabbitMQ."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Připojení k RabbitMQ bylo uzavřeno.")

#==========================================================================
# HANDLER PRO ZPRACOVÁNÍ UDÁLOSTÍ SOUBOROVÉHO SYSTÉMU
#==========================================================================
import hashlib


'''
Třída `Handler` je určena pro sledování událostí souborového systému. 

Používá se v ní `FileSystemEventHandler` pro zachycení změn v konkrétním adresáři. Tato třída také podporuje ukládání PDF souborů nalezených v adresáři a odesílání zpráv do fronty RabbitMQ. 

Hlavní atributy třídy:
- `directory_dog`: Nastavuje se při inicializaci, slouží k uložení cesty k adresáři, kde probíhá sledování. Hodnota je určena funkcí `docker_or_local()`, která nastavuje adresář podle prostředí (Docker nebo lokální).
- `pdf_list`: Prázdný seznam, který uchovává cesty nalezených PDF souborů. Tento seznam se plní při kontrole adresáře pomocí metody `check_directory`.
- `rabbit_connection`: Uchovává instanci připojení k RabbitMQ, kterou třída využívá k odesílání zpráv.
- `filename`: Uchovává název aktuálního zpracovávaného souboru (nastavuje se dynamicky během použití).

Metody:
- `__init__`: Konstruktor třídy `Handler`. Inicializuje výchozí hodnoty a atributy instance.
- `check_directory`: Kontroluje platnost adresáře a prohledává všechny podadresáře pro PDF soubory, které následně přidává do `pdf_list`.
- 'comput_file_hash': 
'''


class Handler(FileSystemEventHandler):

    '''definuj ATRIBUTY INSTANCE'''
    def __init__(self):
        self.directory_dog = docker_or_local()          # Inicializace v konstruktoru
        self.pdf_list = []                              # Seznam pro ukládání nalezených PDF souborů, (soubory ulozen ypred spustenim)
        self.rabbit_connection = RabbitMQConnection()   # Inicializace pripojeni RabbitMq
        self.filename = None                                   # Naplni se pozdeji
    # ==========================================================================
    def check_directory(self):
        directory = self.directory_dog

        # Kontrola, zda je zadaná cesta platný adresář
        if not os.path.isdir(directory):
            raise ValueError('Zadaný adresář neexistuje nebo není přístupný.')

        # Procházení souborů v adresáři i podadresářích
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.lower().endswith('.pdf'):  # Ověření, zda soubor končí na .pdf
                    # Získání absolutní cesty k souboru
                    absolute_path = os.path.join(root, filename)

                    # Přidání absolutní cesty k seznamu pdf_list
                    self.pdf_list.append(absolute_path)
    #root: aktuální adresář, který os.walk() prochází.
    #dirs: seznam podadresářů v aktuálním adresáři.
    #files: seznam souborů v aktuálním adresáři.

    # ==========================================================================
    def comput_file_hash(self, file_path):
        """
        Vypočítá SHA-256 hash zadaného souboru.
        :param file_path: Cesta k souboru, který chcete hashovat.
        :return: Hash souboru ve formátu hexadecimálního řetězce.
        """

        sha256_hash = hashlib.sha256()
        # Otevři soubor v binárním režimu pro čtení dat
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):  # čte v blocích po 4096 bajtech (4 KB)
                sha256_hash.update(byte_block)  # Předání přečteného bloku do hash bloku
        return sha256_hash.hexdigest()

    # ==========================================================================
    def get_file_size(self, file_path):
        '''vrat hodonotu souboru v bytech'''
        try:
            size = os.path.getsize(file_path)
            return size
        except FileNotFoundError:
            print(f"Soubor {file_path} nebyl nalezen.")
            return None
        except Exception as e:
            print(f"Nastala chyba při získávání velikosti souboru: {e}")
            return None

    def get_info(self, event):
        #self.only_filename = os.path.basename(event.src_path)
        self.my_path = event.src_path
        print(f"ted zkus overit self.filename z get_info{self.my_path}")
        print(f"obsah event: {vars(event)}")

    # ==========================================================================
    def simulate_existing_files(self):

        """Projde seznam souborů a simuluje volání on_created pro každý soubor."""
        for file in self.pdf_list:
            event = type('Event', (object,), {'src_path': file, 'is_directory': False})()  # Simulace eventu
            self.on_created(event)

    def _handle_event(self, event, action, message):
        """Pomocná metoda pro zpracování událostí souborů."""

        if not event.is_directory:  # Ignoruje adresáře
            try:
                self.init_message(event, action, message)

            except Exception as e:
                print(f'Chyba při zpracování události: {e}')
    # ==========================================================================
    def on_moved(self, event):
#        if isinstance(event, FileMovedEvent):
            # src: - puvodni cesta source
            # dest: - nova uprava
        #self.get_info(event) # metoda pro nastaveni atribut self.only_filename
        old_filename = os.path.basename(event.src_path)   # puvodni nazev soubory
        print("zde je oldfilename:", old_filename)

        path_complete = event.src_path
        print(f"kompletni cesta v path_complete v on moved{path_complete}")

        new_filename = os.path.basename(event.dest_path) # novy aktualni nazev
        print("Zde je filename",new_filename)

        print(f"Soubor byl přejmenován z {old_filename} na {new_filename}")

        self.init_message(event, "RENAMED", 'Soubor byl přejmenován')

    # ==========================================================================
    def on_created(self, event):
        self.get_info(event)
        self._handle_event(event, "CREATED", 'Soubor byl vytvořen')

    # ==========================================================================
    def on_modified(self, event):
        self.get_info(event)
        self._handle_event(event, "MODIFIED", 'Soubor byl upraven')

    # ==========================================================================
    def on_deleted(self, event):
        self.get_info(event)
        time.sleep(0.1)  # Možná zpoždění pro synchronizaci
        self._handle_event(event, "DELETED", 'Soubor byl smazán')



   # po kontrole odstrani direcoty_patj
    def init_message(self,event, change_type, description, new_filename=None):
        # Celá cesta k souboru (nazev vcetne cesty)

        name_file = event.src_path
        print(f"Over mit filename v ini_messgae {name_file}")

        self.name_file = os.path.basename(name_file)  # název souboru
        print(f"tady over atribut self.name_file{self.name_file}")

        self.path_file = os.path.dirname(name_file)  # cesta k souboru
        print(f"Over cestu souboru: {self.path_file}")

        # Kontrola existence dest_path
        if hasattr(event, 'dest_path') and event.dest_path:
            new_filename = os.path.basename(event.dest_path)
        else:
            print("pouzivam misto dest_path src_path")
            new_filename = self.name_file


        # Generování ID souboru
        file_id = str(uuid.uuid4())

        # Výpočet hash souboru, pokud není smazán nebi prejmenovan protoze jiz hash maji
        hash_item = self.comput_file_hash(name_file) if change_type not in ["DELETED", "RENAMED"] else None

        # Zpracování PDF souboru
        pdf_processor = Pdf_processor()
        kontent = pdf_processor.proces_pdf(name_file) if change_type in ["CREATED", "MODIFIED"] and os.path.exists(name_file) else None

        # Získání velikosti souboru
        size = self.get_file_size(name_file)

        # Příprava metadat
        metadata = {'description': description}
        if change_type == "RENAMED":
            metadata['new_filename'] = new_filename  # Uložení starého názvu pro metadata
            print(f"overeni navratu metadata z old-filename z init_message:{new_filename}")

        # Odeslání zprávy do RabbitMQ
        self.rabbit_connection.send_message(
            file_id=file_id,
            filename=self.name_file,  # Použití názvu souboru
            directory=self.path_file,  # Použití cesty k souboru
            hash_item=hash_item,
            change_type=change_type,
            metadata=metadata,
            size=size,
            kontent=kontent
        )

if __name__ == '__main__':

    w = Watcher()
    w.run()