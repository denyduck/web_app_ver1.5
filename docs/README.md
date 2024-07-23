# Příručka pro Webový projekt Aplikace s Flask, MySQL, Adminer, Nginx, a MkDocs

## Úvod

Tato **příručka** poskytuje přehled a popis serverové části webové aplikace, 
jejímž jádrem je framework **Flask**, databáze **MySQL**, grafický spravce databáze **Adminer**, 
reverzní proxy server **Nginx**, server **Gunicorn** a **MkDocs**. 
Projekt se zaměřuje na vytvoření šablon v různých fáze vývoje pro různě náročné projkety webových aplikací 
od jednoduchých až po komplexní magazín a e-shop.

*Celý projekt bude nasazen v Dockeru, který zajišťuje izolaci, snadnou správu závislostí a snadné nasazení aplikace.*

**Aplikce bude spustitelná na všech zařízení, které podporují kontejnerový engin Docker. To nabízí výhodu i pro vývoj napříč rozdílným systémům
jako je Linux nebo Windows**


## Cíle Projektu

- **Učení a porozumění**: Implementace různých aspektů backendových aplikací.
- **Modularita**: Vytváření komponentů, které lze snadno rozšířit a opakovaně použít.
- **Přehledná dokumentace**: Usnadnění navigace a orientace v dokumentaci projektu.
- **Flexibilita**: Rozšiřování a úpravy podle konkrétních potřeb.



## Jádrem projektu...
### Flask

**Flask** je mikroframework pro Python, který se používá k vytváření webových aplikací a API. Je oblíbený pro svou jednoduchost a flexibilitu.

**Výhody Flasku:**
- **Rychlý vývoj**: Umožňuje rychlé prototypování a vývoj aplikací.
- **Modularita**: Umožňuje snadné přidávání nových funkcí a modulů.
- **Flexibilita**: Nepřesně určuje strukturu aplikace, poskytuje svobodu v návrhu.
<detail>
Flask je ideální pro malé až středně velké aplikace, kde chcete mít plnou kontrolu nad designem a funkcionalitou.

### Gunicorn

**Gunicorn** (Green Unicorn) je WSGI HTTP server pro Python. Používá se pro nasazení Flask aplikací do produkčního prostředí.

**Výhody Gunicornu:**
- **Výkon**: Podporuje vícevláknové zpracování a více workerů, což zvyšuje výkon a škálovatelnost.
- **Stabilita**: Zajišťuje stabilní běh aplikace v produkčním prostředí.
- **Jednoduché použití**: Snadno se integruje s webovými servery jako Nginx.

Gunicorn je ideální pro robustní nasazení aplikací, kde je třeba zpracovávat velké množství požadavků.

### Nginx

**Nginx** je webový server a reverzní proxy server. V kombinaci s Flask a Gunicorn poskytuje:

**Klíčové Funkce Nginx:**
- **Reverzní Proxy**: Předává požadavky od klientů na backendové servery a obsluhuje statický obsah.
- **Load Balancing**: Distribuuje zátěž mezi více instancemi aplikace.
- **Caching**: Ukládá odpovědi do cache pro rychlejší přístup.
- **Bezpečnost**: Zajišťuje TLS/SSL terminaci pro šifrování komunikace.

Nginx zajišťuje efektivní a bezpečné zpracování požadavků, čímž zlepšuje výkon a dostupnost aplikace.

### MkDocs

**MkDocs** je nástroj pro vytváření statických dokumentačních webových stránek z Markdown souborů.

**Výhody MkDocs:**
- **Jednoduchá tvorba dokumentace**: Snadná správa dokumentace pomocí Markdownu.
- **Automatická generace HTML**: Markdown soubory jsou automaticky převedeny na HTML.
- **Přizpůsobitelnost**: Nabízí různé šablony a možnosti konfigurace.

MkDocs je ideální pro projekty, kde je potřeba dobře strukturovaná a snadno dostupná dokumentace.

### MySQL

**MySQL** je relační databázový systém pro ukládání a správu dat. Je široce používaný pro jeho výkon, spolehlivost a flexibilitu.

### Adminer

**Adminer** je grafický správce databází, který poskytuje uživatelské rozhraní pro práci s MySQL databázemi. Umožňuje snadnou správu, vizualizaci a manipulaci s databázovými daty.

### Git

**Git** je verzovací systém pro sledování změn v kódu. 

## Závěrem
