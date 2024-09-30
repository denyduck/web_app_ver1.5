# KONFIGURAČNÍ SOUBOUR FLASK APLIKACE
    # 1. DATABAZE - heslo, nazev db
import os.path  # Importuje modul pro práci s cestami a soubory

# Hlavní třída pro konfiguraci aplikace
class Config:
    SECRET_KEY = "my_password"  # Tajný klíč pro ochranu sessions a cookies
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Zabraňuje SQLAlchemy v sledování změn v objektech (výkonová optimalizace)
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://root:root_password@db/my_database'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://my_user:my_password@localhost/my_database' # localhost bez DOCKERU
#'mysql+pymysql://root:root_password@db/my_database'   # URI pro připojení k databázi při vývoji

'''# Konfigurace pro vývojové prostředí
class Development_config(Config):
    SQLALCHEMY_DATABASE_URI =   # URI pro připojení k databázi při vývoji
'mysql+pymysql://root:root_password@db/my_database'
# Konfigurace pro Docker prostředí
class Docker_config(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://my_user:my_password@db/my_database'  # URI pro připojení k databázi v Dockeru (služba je přístupná pod názvem 'db')

# Funkce pro kontrolu, zda je aplikace spuštěna v Dockeru
def is_running_in_docker():
    return os.path.exists('/.dockerenv')  # Zkontroluje, zda existuje soubor '.dockerenv', což indikuje, že aplikace běží v Dockeru

# Funkce pro získání správné konfigurace na základě prostředí
def get_config():
    if is_running_in_docker():
        return Docker_config()  # Pokud je aplikace v Dockeru, vrátí Docker_config
    else:
        return Development_config()  # Jinak vrátí Development_config

# Získání aktuální konfigurace
config = get_config()

# Výpis aktuálně používané databázové URI
print(f'Pohybujes se v prostred: {config.SQLALCHEMY_DATABASE_URI}')'''