#==========================================================================
# Importy
#==========================================================================

# Importuje moduly pro manipulaci se soubory a čas
import os
import time  # Modul pro čekání během běhu programu

# Importuje moduly pro práci s RabbitMQ
import pika

# Import pro získání správného adresáře (lokální nebo Docker)
from config_watchdog import docker_or_local

# Import pro zpracování událostí systému souborů
from watchdog.events import FileSystemEventHandler          # Zpracovává události (např. změna souborů)
from watchdog.observers.polling import PollingObserver      # Sledování změn souborového systému

# Importuje moduly pro generování unikátních ID
import uuid

# Import pro odesílání zpráv do RabbitMQ
from send_message import send_file_event
from message import new_message

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

        self.extract_kontent = None  # nejdrive se bude nastavavovat atribut, proto pocatecni None

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
    def send_message(self, file_id, filename, directory, file_hash, change_type, metadata, kontent):
        self.file = filename

        """Odešle zprávu o změně souboru do fronty RabbitMQ."""
        if self.channel is None or not self.channel.is_open:
            print("Připojení není otevřené, pokusím se znovu připojit.")
            self.connect()

        try:
            # Vytvoř zprávu
            message = new_message(self.message_id, filename, directory, file_hash, change_type, metadata, kontent)
            print(f"Zpráva vytvořena: {message}")

            # Odeslání zprávy
            send_file_event(file_id, change_type, self.channel, message)
            print(f"Zpráva odeslána pro soubor: {filename}")
        except Exception as e:
            print(f'Chyba při odesílání zprávy: {e}')
        finally:
            self.close()
    def get_pdf_name(self):
        return self.file


    # ==========================================================================
    def close(self):
        """Uzavře připojení k RabbitMQ."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Připojení k RabbitMQ bylo uzavřeno.")


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
# HANDLER PRO ZPRACOVÁNÍ UDÁLOSTÍ SOUBOROVÉHO SYSTÉMU
#==========================================================================
import hashlib


class Handler(FileSystemEventHandler):

    def __init__(self):
        self.directory_dog = docker_or_local()          # Inicializace v konstruktoru
        self.pdf_list = []                              # Seznam pro ukládání nalezených PDF souborů, (soubory ulozen ypred spustenim)
        self.rabbit_connection = RabbitMQConnection()   # Inicializace pripojeni RabbitMq

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
    def check_directory(self):
        directory = self.directory_dog

        # Kontrola, zda je zadaná cesta platný adresář
        if not os.path.isdir(directory):
            raise ValueError('Zadaný adresář neexistuje nebo není přístupný.')

        # Procházení souborů v adresáři
        for filename in os.listdir(directory):
            if filename.lower().endswith('.pdf'):  # Ověření, zda soubor končí na .pdf
                # Přidání plné cesty k souboru do seznamu pdf_list
                self.pdf_list.append(os.path.join(directory, filename))



    # ==========================================================================

    def send_messeage(self, event, change_type, description, directory_path):

        pdf_processor = Pdf_processor()
        file_id = str(uuid.uuid4())
        filename = event.src_path.split("/")[-1]
        directory = directory_path.rsplit("/", 1)[0]
        file_hash = self.comput_file_hash(event.src_path) if change_type != 'del' else None
        # Použití obsahu z extrahovaného textu, pokud je to nová nebo editovaná změna
        # Nejprve zavolej metodu ex_path s parametrem pro cestu souboru, aby nastavila atribut 'extract_kontent' pro pouziti zde

        kontent = pdf_processor.proces_pdf(event.src_path) if change_type in ['new', 'edit'] else None

        # Odeslani zprávy do RabbitMq
        self.rabbit_connection.send_message(
            file_id = file_id,
            filename = filename,
            directory=directory,
            file_hash=file_hash,
            change_type=change_type,
            metadata={'description':description},
            kontent=kontent
        )

    # ==========================================================================
    def simulate_existing_files(self):
        """Projde seznam souborů a simuluje volání on_created pro každý soubor."""
        for file_path in self.pdf_list:
            event = type('Event', (object,), {'src_path': file_path, 'is_directory': False})()  # Simulace eventu
            self.on_created(event)  # Volání metody on_created pro simulovaný event

    # ==========================================================================
    def on_created(self, event):
        if not event.is_directory:  # Ignoruje adresáře
            try:
                self.send_messeage(event, 'new', 'Soubor byl vytvořen', event.src_path)
            except Exception as e:
                print(f'Chyba při vytváření souboru: {e}')

    # ==========================================================================
    def on_modified(self, event):
        if not event.is_directory:  # Ignoruje adresáře
            try:
                self.send_messeage(event, 'edit', 'Soubot byl upraven', event.src_path)
            except Exception as e:
                print(f'Chyba při zpracování úprav souboru: {e}')

    # ==========================================================================
    def on_deleted(self, event):
        if not event.is_directory:  # Ignoruje adresáře
            time.sleep(0.1)
            try:
                self.send_messeage(event, 'del', 'Soubor byl smazán', event.src_path)
            except Exception as e:
                print(f'Chyba při zpracování mazání souboru: {e}') # vola fci pro odkazovani na instanci tridy

    # ==========================================================================
    def on_moved(self, event):
        """Tato metoda je volána při přesunu souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            try:
                self.send_messeage(event, 'del', 'Soubor byl přesunut nebo přejmenován', event.src_path)
                event.src_path = event.dest_path

                self.send_messeage(event, 'new', 'Soubor byl přesunut - nová cesta', event.src_path)

            except Exception as e:
                print(f'Chyba při zpracování přesunutí souboru: {e}')


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


#==========================================================================


if __name__ == '__main__':

    w = Watcher()
    w.run()