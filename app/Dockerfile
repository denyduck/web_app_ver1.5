# Dockerfile pro flask aplikace


# verze balíčku
FROM python:latest

# nastavení pracovního adresáře uvnitř kontejneru
WORKDIR usr/src/app

# zkopirovani souboru v umisteni dockerfile do pracovniho adresare
COPY . . 

# instalace závistlostí z requirements.txt
RUN pip install -r requirements

# spuštění aplikace
# spusti python s hodnou runn.py
CMD ["python", "runn.py"]

