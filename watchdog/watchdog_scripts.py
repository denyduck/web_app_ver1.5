import os
import time  # Importuje modul time pro čekání během běhu programu
import requests  # Knihovna pro odesílání HTTP požadavků (pro API, zde pro FLASK)

# z lokalního adresare pro kontener - mimo kontex projektu!
from config_watchdog import docker_or_local

from watchdog.observers import Observer  # Observer sleduje změny v souborovém systému
from watchdog.events import FileSystemEventHandler  # FSWH zpracovává události (např. změna souborů)

from watchdog.observers.polling import PollingObserver # z dovudu nekonzistentnich souborovych systemu na ruznych systemech


#directory_dog = docker_or_local()
directory_dog = docker_or_local()

# Debug výstup

print("Načtení skriptu ..")
print(directory_dog)


# Pro výpis všech souborů v adresáři
for filename in os.listdir(directory_dog):
    if filename.endswith(".pdf"):
        print(f"PDF soubor nalezen: {filename}")



class Watcher:

    def __init__(self):
        """Konstruktor třídy Watcher. Vytvoří instanci Observer."""
        #self.observer = Observer()
        self.directory_dog = directory_dog
        self.observer = PollingObserver()
    def run(self):
        """Inicializuje sledování a spouští sledování změn v adresáři."""
        event_handler = Handler()  # Vytvoří instanci handleru

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




class Handler(FileSystemEventHandler):
    """Třída Handler zpracovává události, které nastanou v sledovaném adresáři."""

    def on_created(self, event):
        """Tato metoda je volána při vytvoření nového souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            try:
                print(f'Soubor {event.src_path} byl vytvořen!')  # Debug output
                requests.post('http://nginx/requests/file_dog', json={'file': event.src_path})
            except Exception as e:
                print(f'Chyba při zpracování vytváření souboru: {e}')

    def on_modified(self, event):
        """Tato metoda je volána při modifikaci existujícího souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            try:
                print(f'Soubor {event.src_path} byl upraven!')  # Debug output
                #requests.post('http://nginx/requests/file_dog', json={'file': event.src_path})
            except Exception as e:
                print(f'Chyba při zpracování úprav souboru: {e}')


    def on_deleted(self, event):
        """Tato metoda je volána při smazání souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            try:
                print(f'Soubor {event.src_path} byl smazán!')  # Debug output
                #requests.post('http://nginx/requests/file_dog', json={'file': event.src_path})
            except Exception as e:
                print(f'Chyba při mazání soubor: {e}')

    def on_moved(self, event):
        """Tato metoda je volána při přesunu souboru."""
        if not event.is_directory:  # Ignoruje adresáře
            try:
                print(f'Soubor {event.src_path} byl přejmenován {event.dest_path}!')  # Debug output
                #requests.post('http://nginx/requests/file_dog', json={'file': event.src_path})
            except Exception as e:
                print(f'Chyba při zpracování přesunutí souboru: {e}')

if __name__ == '__main__':
    w = Watcher()
    w.run()