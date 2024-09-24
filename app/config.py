# KONFIGURAČNÍ SOUBOUR FLASK APLIKACE
    # 1. DATABAZE - heslo, nazev db
class Config:
    SECRET_KEY = "my_password"
    SQLALCHEMY_DATABASE_URI = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = ""

    PDF_DIRECTORY = "./pdfs"
