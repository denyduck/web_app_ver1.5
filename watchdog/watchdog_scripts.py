import os
import time  # Importuje modul time pro čekání během běhu programu
import requests  # Knihovna pro odesílání HTTP požadavků (pro API, zde pro FLASK)

from watchdog.observers import Observer  # Observer sleduje změny v souborovém systému
from watchdog.events import FileSystemEventHandler  # FSWH zpracovává události (např. změna souborů)

print("Načtení skriptu...")

class Watcher:
    DIRECTORY_TO_WATCH = '/usr/src/pdfs'  # Sledovaný adresář

    def __init__(self):
        """Konstruktor třídy Watcher. Vytvoří instanci Observer."""
        self.observer = Observer()

    def run(self):
        """Inicializuje sledování a spouští sledování změn v adresáři."""
        event_handler = Handler()  # Vytvoří instanci handleru
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        print(f"Sledování adresáře: {self.DIRECTORY_TO_WATCH}")  # Debug output
        self.observer.start()  # Spustí sledování adresáře

        try:
            while True:
                time.sleep(2)  # Program běží
                print("Skript běží...")
        except KeyboardInterrupt:
            self.observer.stop()  # Ošetření výjimky
            print("Observer STOPPED!")
        self.observer.join()  # Čeká, dokud není sledování ukončeno

class Handler(FileSystemEventHandler):
    """Třída Handler zpracovává události, které nastanou v sledovaném adresáři."""

    def on_created(self, event):
        """Tato metoda je volána při vytvoření nového souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            print(f'Soubor {event.src_path} byl vytvořen!')  # Debug output
            requests.post('http://nginx/requests/file_dog', json={'file': event.src_path})

    def on_modified(self, event):
        """Tato metoda je volána při modifikaci existujícího souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            print(f'Soubor {event.src_path} byl upraven!')  # Debug output
            requests.post('http://nginx/requests/file_dog', json={'file': event.src_path})

    def on_deleted(self, event):
        """Tato metoda je volána při smazání souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            print(f'Soubor {event.src_path} byl smazán!')  # Debug output
            requests.post('http://nginx/requests/file_dog', json={'file': event.src_path})

    def on_moved(self, event):
        """Tato metoda je volána při přesunu souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            print(f'Soubor {event.src_path} byl přesunut na {event.dest_path}!')  # Debug output
            requests.post('http://nginx/requests/file_dog', json={'file': event.src_path})

if __name__ == '__main__':
    w = Watcher()
    w.run()