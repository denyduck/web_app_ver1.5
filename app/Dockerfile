# Dockerfile pro flask aplikace


# verze balíčku
FROM python:latest

# nastavení pracovního adresáře uvnitř kontejneru
WORKDIR /usr/src/app

# zkopirovani souboru v umisteni dockerfile do pracovniho adresare
# z důvodu kešování jsou copy odděleny, pokud se nezmění nemus se kešovat znovu a uštří čas
COPY requirements.txt ./

# zkopíruje ostatní soubory do pracovního adresáře kontejneru
COPY . .

# instalace závistlostí z requirements.txt, cache nebude ukládána (ušetří místo v kontejnerech a na serveru
RUN pip install --no-cache-dir -r requirements.txt

# spuštění aplikace
# spusti python s hodnou run.py
CMD ["python", "run.py"]

