# Koncept rozložení
## Blueprint - ADMIN
### Modul /prohlizet.html
Cílem modulu, je vrátit uživateli co nejrychleji data. Nejrychleji proto, že se očekává servírování dokumentu v řádech nižších stovek.


Mohu jej zpracovat dvěma přístupy:

1. Server-Site Rendering - Server IN  
   [ ] Zpracování dat serverem, vrácení hotových dat do html, kde se pomocí smyčky for načtou

Uživatel uvidí stránku téměř okamžitě, protože server vrátí kompletní HTML s načtenými základními daty.
To je užitečné pro zajištění rychlého "prvního zobrazení", což je důležité pro SEO i uživatelskou spokojenost.

2. Client-Site Rendering - Server OUT  
   [ ] Po načtení základních dat můžete přidat interaktivní prvky, jako je například zobrazení detailů, náhledů souborů, filtrování dat nebo jiné dynamické funkce.
Tento přístup je velmi flexibilní a umožňuje přidávat nové funkce bez nutnosti měnit celý backend.


