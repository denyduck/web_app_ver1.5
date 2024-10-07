import os
import time  # Importuje modul time pro čekání během běhu programu
import requests  # Knihovna pro odesílání HTTP požadavků (pro API, zde pro FLASK)
import pika
# z lokalního adresare pro kontener - mimo kontex projektu!
from config_watchdog import docker_or_local
from tools import ex_path
from watchdog.events import FileSystemEventHandler  # FSWH zpracovává události (např. změna souborů)


from watchdog.observers.polling import PollingObserver # z dovudu nekonzistentnich souborovych systemu na ruznych systemech

import uuid

from send_message import send_file_event
from message import new_message

message_id = str(uuid.uuid4())


#directory_dog = docker_or_local()
directory_dog = docker_or_local()

# Debug výstup

print("Načtení skriptu ..")
print(directory_dog)



#==========================================================================
# ZISKANI DAT Z ENV, PRIPOJENI K RABBITMQ-KANAL, ODSLANI ZPRAVY
#==========================================================================
def connect_and_message(file_id, filename, directory, hash, change_type, metadata, kontent):
    connection = None        # inicializace na None, zajistuje ze promena existuje ikdyz pripojeni selze

    try: # ostereni vyvovlani vyjimky, preskoc na except

        '''prihlasovaci udeje'''
        credentials = pika.PlainCredentials(             # prihlasovaci udaje
            os.getenv('RABBITMQ_USER', 'user'),          # nacti z compose/.env, pokud nic tak user
            os.getenv('RABBITMQ_PASSWORD', 'password'))  # stejne

        '''pripojeni'''
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),    # prihlasovaci udaje, pokud nejsou default: rabbitmq
            port=int(os.getenv('RABBITMQ_PORT', '5672')),   # port jinak default 5672
            credentials=credentials))

        '''vytvor kanal'''
        channel = connection.channel()      # vytvori kanal pro komunikaci

        '''vytvor frontu do kanalu a nastav ji'''
        channel.queue_declare(
            queue='file_events',    # fronta s nazvem file_events
            durable=True)           # True = fronta přezije restart kontejneru

        '''Vytvoř zpravu a napln ji'''
        make_messeage = new_message(message_id, filename, directory, hash, change_type, metadata, kontent)
        print(make_messeage)     # Debug

        '''odesli zpravu zabalenou s oznacenim hlavicky file_id a typem zpravy'''
        sending_messeage = send_file_event(file_id, change_type, channel, make_messeage)
        print(type(sending_messeage))     # Debug



    except Exception as e:                          # pokud dojde k chybě v bloku try:
        print(f'Chyba při zpracování zprávy: {e}')  # vraci chybu


        '''uzavris spojeni v pripade:'''
        # chyby
        if connection and connection.is_open:
            connection.close()

    # po uspesnem odeslani
    if connection and connection.is_open:  # Zkontroluje, zda je připojení otevřené
        connection.close()  # Uzavření spojení




import hashlib

# vypocita hash pro soubor
def comput_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    # otevri soubr v binarnim rezimu pro cteni dat i binarnich
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):  # čte v blocích po 4096 bajtech (4 KB)
            sha256_hash.update(byte_block)  # predani precteneho bloku do hash bloku
    return sha256_hash.hexdigest()


#==========================================================================
# HANDLER PRO ZPRACOVÁNÍ UDÁLOSTÍ SOUBOROVÉHO SYSTÉMU
#==========================================================================
class Handler(FileSystemEventHandler):

    def __init__(self):
        self.directory_dog = docker_or_local()  # Inicializace v konstruktoru
        self.pdf_list = []  # Seznam pro ukládání nalezených PDF souborů
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

        file_id = str(uuid.uuid4())
        filename = event.src_path.split("/")[-1]
        directory = directory_path.rsplit("/", 1)[0]
        file_hash = comput_file_hash(event.src_path) if change_type != 'del' else None # pri zmenach krome smazani souboru
        kontent = ex_path(event.src_path) if change_type in ['new', 'edit'] else None

        connect_and_message(
            file_id = file_id,
            filename = filename,
            directory=directory,
            hash = file_hash,
            change_type=change_type,
            metadata={'description':description},
            kontent=kontent
        )
    # ==========================================================================
    def sync_with_databses(self):
    # zpracovani souboru, pokud jsou pritomni jiz v adresari
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