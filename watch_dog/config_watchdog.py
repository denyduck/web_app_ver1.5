from dotenv import load_dotenv
import os

# Načte proměnné z .env souboru
load_dotenv('../.env')

#Zobrazte všechny načtené proměnné prostředí
for key, value in os.environ.items():
    print(f'{key}: {value}')



# Získání proměnných prostředí
local_dog_directory = os.getenv('LOCAL_DOG_DIRECTORY')
#local_dog_directory = r'C:/Users/d.matyus/OneDrive - Maspex Wadowice/Plocha/my/web_app_ver1.3/pdfs'
print(f'toto je local{local_dog_directory}')


docker_dog_directory = os.getenv('DOCKER_DOG_DIRECTORY')
# docker_dog_directory = '/usr/src/app/pdfs'
print(f'toto je docker{docker_dog_directory}')


is_docker = os.getenv('IS_DOCKER', 'false').lower() == 'true'  # Zajištění výchozí hodnoty
print(f'toto je: {is_docker}')

def docker_or_local():
    # Rozhodnutí, kterou cestu použít na základě toho, zda běžím v Dockeru
    if is_docker:
        directory_dog = local_dog_directory
    else:
        directory_dog = docker_dog_directory
    return directory_dog

# Debug výstup
print(f'Adresář v configu: {docker_or_local()}')