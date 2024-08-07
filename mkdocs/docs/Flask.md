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

### 3. Rozdělení aplikace pomocí Blueprintů

Použití blueprintů pro rozdělení aplikace zvyšuje její přehlednost a škálovatelnost. Blueprinty umožňují modularizaci a organizaci kódu, což usnadňuje údržbu a rozšiřování aplikace. V rámci této aplikace budou použity následující blueprinty:

1. **Admin Blueprint**
    - **Popis**: Tento blueprint bude zodpovědný za správu administrativních funkcí aplikace. Může obsahovat administrativní rozhraní, nástroje pro správu uživatelů, reporty a další administrativní funkce.
    - **Příklad**: `/admin`, `/admin/users`, `/admin/reports`

2. **Users Blueprint**
    - **Popis**: Tento blueprint bude zaměřen na správu uživatelských funkcí. Bude zahrnovat funkce jako registraci, profil uživatele, správu uživatelských nastavení a další uživatelsky orientované funkce.
    - **Příklad**: `/users/profile`, `/users/settings`, `/users/notifications`

3. **Authenticate Blueprint**
    - **Popis**: Tento blueprint se zaměří na autentizaci a autorizaci. Bude zahrnovat přihlašování, odhlašování, registraci nových uživatelů a správu uživatelských relací.
    - **Příklad**: `/auth/login`, `/auth/logout`, `/auth/register`

4. **Public Blueprint**
    - **Popis**: Tento blueprint bude obsahovat veřejné části aplikace, které jsou dostupné bez potřeby přihlášení. Může zahrnovat stránky jako úvodní stránku, kontaktní informace, blogové příspěvky a další veřejně přístupný obsah.
    - **Příklad**: `/`, `/about`, `/contact`


    ![diagram](http://localhost:8081/svg/bP9BRWCX38RtEGKNIBlFebAYAEgYYwfILX4QCU1cK1cCZ56kr7FqP1r8CdbLOieAR7_sRnksx60XLYv18EjPHAQaEH7CPc8ukurJyKiiGt1MAxRefPWRFFZvYzWjJM_zXPLrOXk1uXKX9XH939wp7Vu7lgTsiDumfvxkTL-OjOfTYugCh4MguYdzJ8jjDFhSYImYZiZ3E4Ra5NkGOY6Uk-7or77lQaJsD6RGZstMVyF-VDTeCCS91y9Fwz9TwVFS_bx5cEG3zZOoKA4fFqZfQ_Mr16-ujxxGBjzEnGlwkCsH2iNLg1RJ-GzMe-Naj14KwKxcdVq2)


##### Vytvoření Blueprintu ADMIN - struktura adresářů a souborů

1. **Vytvořím adresář:**
    - Vytvořím nový adresář **`admin`** v adresáři **`app`**.

2. **Vytvořím soubory:**
    - V adresáři **`app/admin`** vytvořím soubory:
     - `__init__.py`
     - `views.py`

3. **Vytvořím adresář pro šablony:**
    - Vytvořím adresář **`templates`** v **`app/admin`**.

4. **Vytvořím šablonu:**
    - V adresáři **`templates`** umístím soubor **`dashboard_admin.html`**.

##### Konfigurace Inicializačního Souboru

Inicializační soubor **`__init__.py`** slouží k registraci Blueprintu a jeho konfiguraci. Tento soubor by měl obsahovat následující kód:

```python
from flask import Blueprint

# Vytvoření Blueprintu
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# Importování pohledů
from . import views

from flask import Blueprint

# vytvoření BP pro registrace stranek html ve views
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# po registraci BP načíst cesty html soubrů z views (pro oddělení views a reg.BP)
from app.admin import views

```

  