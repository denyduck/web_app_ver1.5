# Mini framework FLASK

**Flask je nasazen na Gunicorn server, který ji spouští a obshluje HTTP požadavky**

### Vytvoření
Pro jednodušší zprávu a údržbu aplikace oddělím nastavení aplikace od jejího kodu. Konfigurační soubor `config.py**` 
bude obsahovat různé proměnné a nastavení, která aplikace potřebuje. Mohou to být například cesty k souborům, 
proměnné, přihlašovací údaje k databázi, klíče API a další.
---

#### 1. Vytvoření konfiguračního souboru

Konfigurační soubor bude uložen v kořenovém adresáři **/app/config.py** 

```python
import os

class Config:
    SECRET_KEY = ....   # Klíč pro šifrování session dat
    DATABASE_URL = .... # URL pro připojení k databázi
    DEBUG = ....    # Nastavení režimu ladění
```

---

#### 2. Inicializace instance aplikace Flask
Standartní přístup k inicializaci aplikace Flask v moderních aplikací.
Umožnuje centrálně spravovat nastavení aplikace a její komponenty. Probíhá v modulu
`__init__.py` v kořenovém adresáři `webapp/__init__.py`.

_Vytvoření instance:_

```python
app = Flask(__name__, instance_relative_config=False)
# name: hledá zdrojové soubory 
# instance_relative_config: říká Flasku, že konfigurační soubory se nachází v cestě zadané v from_object, nikoliv relativně k instanci aplikace.
```
_Načtení konfigurace z objektu `Config`, který je definován v `config.py` v kořenovém adresáři._

```python
app.config.from_object("config.Config")
```

_Přidání zavyslostí a dalšího kontentu:_

```python
from . import routes
```

---