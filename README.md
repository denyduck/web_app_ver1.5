# WEBAPP TEMPLATES

**Projekt se zabývá vytvořením šablon serverové části kodu webových aplikací pro budoucí nasazení v komerčním použíti. Vytvoří se několik verzí projektu od nejméně složitého jako běžná webová aplikace po složitější kterou bude webový magazín nebo eshopové řešení. Každá verze bude uložena jako šablona, tak aby byla samostatně použitelná.**

## Cíle

Cílem tohoto projektu je postupně vybudovat komplexní backendovou aplikaci, přičemž každy krok zahrnuje jak vytvoření jednotlivých částí systému tak i dokumentaci k šabloně. Tento přístup má několik specifických cílů:

### Dílčí cíle:

#### Učení a porozumění
- Pochopit a implementovat různé aspekty backendových aplikací.

#### Modularita
- Vytvářet komoponenty, které mohou být snadno rozšířeny nebo opakovaně použity v různých projektech

#### Přehledná dokumentace
- Usnadnit navigaci a porozmění každému kroku v projektu
- udržování čitelnosti a přehlednosti
- Vytvářet jasnou a přehlednou dokumentaci

#### Praktická zkušnost

#### Flexibilita
- rozšiřování a upraveni podle kontkrétnách potřeb

## Struktura projektu

- [Git, GIThub](#GIT)
- [Docker, nasazení aplikace ](#DOCKER)
- [Projektový adresář](Projektovy_adresar.md)
- [Frontend](#frontend)
- [Backend](#backend)
- [Database](#database)
- [API](#api)
- [Backup](#backup)
- [Testování](#testovani)

- [GitHub](#github)
- [Návrh tříd a diagramy](#navrh-trid-a-diagramy)

## GIT

- projekt bude versován na Github.
- použije se několik větví:

> 1. main - hlavní větev
> 2. develop - vývojřská větev, která zahrnuje celky
> 3. funkce develop - poddružná větev DEVELOPu pro vývoj jednotlivých funkcí, metod


## DOCKER

### dockerfile
Aplikace se nasazuje v kontejneru s dalšími zavislostmi, které jsou pro běh serveru nutné. Samotná aplikace bude konfigurovaní v souboru dockerfile. Zahrnuje napřiklad instalaci všech *requirements, app path, verze balíčků atd*

### docker-compose.yml
Pro nasazení vytvořeného předsloženého *image* z dockerfile se vytvoří spouštěcí script docker-compose.yml. Ten nasazuje samotne kontejnery do jedné aplikace, které mezi sebou z manageruje. 



