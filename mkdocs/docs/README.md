# Příručka pro WebAPP


> ## Verze: 1.0
> Verze obsahuje tyto aplikace v struktuře:

> 1. Docker - vytvoření image pro kontejnery
> 2. Docker_compose - konfigurace a nasazení do kontejnerů
> 2. Git - main, develop
> 3. Nginx - proxy server (obecné nastavení)
> 4. Gunicorn - python server (obecné nastavení pro běh aplikace)
> 5. Flask - jádro aplikace, strukturalizace adresářu
> 6. Mkdocs - generování příručky
> 7. Plantuml - server pro generování diagramu z uml kodu
> 8. adminer - GUI správce databáze
> 9. MYSQL - databázový server  

### Obsah aplikace: ###
**Nginx, Gunicorn, web-flask, mysql, adminer, mkdocs, dockerfile, docker-compose, uml diagramy**  

**Příručka** poskytuje přehled a popis webové aplikace, 
jejímž jádrem je framework **Flask** databáze **MySQL**, grafický spravce databáze **Adminer**, 
reservní proxy server **Nginx**, server **Gunicorn** a **MkDocs**. 
Projekt se zaměřuje na vytvoření šablon v různých fáze vývoje pro různě náročné projkety webových aplikací 
od jednoduchých až po komplexní magazín, e-shop či jinou webovou aplikaci.

## Cíle Projektu

V rámci projektu se zaměřuji na několik klíčových cílů, které mi pomohou vytvořit efektivní a škálovatelné webové řešení. Tyto cíle zahrnují:

### Vývoj
  - **Integrované prostředí**: Zajistit, aby projekt fungoval jak na Windows, tak na Linuxu. To zahrnuje konfiguraci vývojového prostředí a testování kompatibility napříč různými platformami.
  - **Cross-platformní podpora**: Usnadnit vývoj při práci v různých operačních systémech a zajistit, že aplikace bude správně fungovat v obou prostředích.

### Nasaditelnost 
  - **Server s Linux distribucí**: Připravit a nasadit aplikaci na server s Linux distribucí, což zahrnuje instalaci a konfiguraci potřebných závyslostí a zajištění bezproblémového běhu aplikace na produkčním serveru.
  - **Automatizace nasazení**: Implementovat nástroje a skripty pro automatizaci procesu nasazení, čímž se sníží riziko chyb a zjednoduší údržba.

### Učení a porozumění ###
  - **Backendové aplikace**: Hlavním cílem je implementace různých aspektů backendových aplikací, jako jsou API, správa databází a bezpečnostní opatření. Projekt poskytne příležitost k prohloubení znalostí v těchto oblastech.
  - **Praktická zkušenost**: Získat praktické zkušenosti s moderními technologiemi a nástroji, které jsou relevantní v současném vývoji webových aplikací.

### Modularita
  - **Komponenty**: Vytvářet a spravovat komponenty, které jsou snadno rozšiřitelné a opakovaně použitelné v různých částech projektu nebo v budoucích projektech.
  - **Design**: Navrhnout systém tak, aby byl dobře strukturovaný a snadno udržovatelný, což usnadní budoucí úpravy a rozšíření.

### Přehledná dokumentace
  - **Navigace a orientace**: Poskytnout jasnou a přehlednou dokumentaci, která usnadní orientaci v projektu, a to nejen pro současné členy týmu, ale i pro nové vývojáře.
  - **Kompletní pokrytí**: Zahrnout všechny důležité aspekty projektu, od instalace a konfigurace až po použití a údržbu.

### Flexibilita
  - **Rozšiřitelnost**: Navrhnout aplikaci tak, aby byla flexibilní a mohla být snadno přizpůsobena specifickým potřebám a požadavkům uživatelů.
  - **Adaptabilita**: Schopnost reagovat na měnící se požadavky a přizpůsobit se novým technologiím potřebám bez výrazných zásahů do základní struktury projektu.



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
## Náhled dokumentu

[pdf-embedder url="/pdf/document1.pdf"]

### Adminer

**Adminer** je grafický správce databází, který poskytuje uživatelské rozhraní pro práci s MySQL databázemi. Umožňuje snadnou správu, vizualizaci a manipulaci s databázovými daty.

### Git

**Git** je verzovací systém pro sledování změn v kódu. 

## Závěrem

![Diagram](http://localhost:8081/svg/ZLLHQzim47xFhpZwj1b20sMZx64G6ke46l2QTdqeOoZosH6sfLIIcuRH_xwJqZgMxTBunKZVwTDzzvtFMyOBbYESJJNV28lSrXhFuDy8w94g9MIcU85whenr-oEFkETHvaA-m9MIbWc9-W-Cnp_XCQ-bu4hBDl03hfNUCPqQqFXKex7cI3Dqm3FjSFqtAvafGgfxWmOofU5X5I-ED8FHdgVQcwSovBX5bfhp1qsA3QJCiYDFBzfpiBHogo6Mtm9t1nBu4jyllhQeYbHnSwgkC2TtS9eant9BPH5Ap2oeh5_x9WmWYZfW5BNGCTtpZDeW95gzx665cfP1m9p9jAGSXEIALETzprnKpr6m2k8tBvj8bAdFlAD3Ytnp43BWVg0bxk4TEQuBO7vtbmn9kQsbWMHlDqe2bHtOTbiApgnGqWng9iMLkz67m1hj3l5mr7XseBWsosT26yDwlH2eN1Qp08qY2D8ZjAwGG9zMZ1J2h0grlkqUcgSLdMbLWTqW65LhZYIHlcfAgMd3apKCDMuWupe4kqvH5QS3fNFOZJ0MoIlADueIfIrycqmc7O9tavmTJTSvGxYIaaQNRy7bVlNh9ZZc1mPdd4hWniOMDRqg9ZcUxbvdA8JckHi_L3sZmR1czBqDj6TVzSN5v7k7O4L6au1MquKJwxFS-wCho7xQXJ_AVyaa_IbSNy52MYeYQnLmMCtbvBBh8KsTPv6I7XgLtexGhqQCMxoENly3)