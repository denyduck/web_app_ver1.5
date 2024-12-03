'''
REGISTRUJ STRANKY DO BP ADMIN
- zakladni roozvrzeni stranky vychazi z base respektive z base_inside ->pro stranky uvnitr,
a z base_outside.

- po rozvrzeni v base se html selektuje do jednotlivych maker
- makra se prekopiruji do "macros_jinja"
- nyni mohou byt jednotliva makra pouzita v ruznych strankach pomoci jinja tagu
- pretezovani zavyslosti maker


1. IMPORTY zavyslosti
2. REGISTRACE potřebnych <page>.html do obsahu blueprintu
    2.1 base_admin - rozlozeni, navrh pro odvozeni maker
    2.2 home
    2.3 *Testování BASE pred nasazením

'''
import logging

'''
REGISTRUJ STRANKY DO BP ADMIN
1. IMPORTY zavyslosti
2. REGISTRACE potřebnych <page>.html do obsahu blueprintu
    2.1 base_admin - rozlozeni, navrh pro odvozeni maker
    2.2 home
    2.3 *Testování BASE pred nasazením

'''

# 1. IMPORTY
from flask import render_template, request, jsonify
from shared_models.rabbit_models import Files
from shared_models import session,Session
from app.routes.admin import admin_bp

import re




# 2. REGISTRACE
# 2.1 Templates - routes
#   2.1.1 def home
#       - vrat z request hodnotu paramatetru "query" a metodou 'strip' odstran mezery, cele to uloz do "query"
#       - vytvor prazdny seznam pro jeho naplneni
#       - pokud je "query" platne, do 'results' uloz vsechny polozky z tabulky Files, kde metoda "like" odpovida retezci shode v 'kontent' a 'filename'
#       - cyklus pro kazde 'r' v 'results pridej polozku po polozce do seznamu 'results_list'
#       - renderuj sablonu s vysledkama, tak aby sli pouzit v html
#   2.1.2 def autocomplete
#       - fce, pro poskytnutí dynamických návrhu uživateli behem psani do vyhledavaciho pole, slouzi jako NASEPTAVAC
#       -
#   2.1.3 def prohlizet
#   2.1.4 def intra
#   2.1.5 def o_projektu

##

@admin_bp.route('/')
def home():
    query = request.args.get('query', '').strip()  # Odstraní nadbytečné mezery z query
    results_list = []  # Inicializace seznamu výsledků

    if query:  # Pokud query není prázdné, provede dotaz
        # Hlavní vyhledávání v obsahu a názvech souborů
        results = session.query(Files).filter(Files.kontent.like(f'%{query}%') | Files.filename.like(f'%{query}%')).all()

        if results:  # Pokud jsou nalezeny výsledky, zpracuje je
            for r in results:
                results_list.append({
                    'filename': r.filename,    # Přidá název souboru
                    'directory': r.directory,  # Přidá adresář
                    'content': r.kontent       # Přidá obsah souboru (pokud je potřeba)
                })

    # Renderuje šablonu a předává výsledky a query
    return render_template('home.html', results=results_list, query=query)

#=========================================================================================================
@admin_bp.route('/autocomplete')
def autocomplete():

    query = request.args.get('query', '').strip().lower()
    results = []

    session = Session() # vytvoreni nove session pro okamzity progres
    try:
        if query:
            # Vyhledávání na základě názvu souboru nebo obsahu
            results = session.query(Files).filter(
                Files.filename.like(f'%{query}%') | Files.kontent.like(f'%{query}%')
            ).all()
            logging.info("Nalezene vysledky: %s", results)
    finally:
        session.close()

    # Vrátíme návrhy jako JSON, včetně 'directory'
    return jsonify([
        {
            'filename': file.filename,
            'kontent': file.kontent[:200] if file.kontent else '',
            'directory': file.directory[file.directory.find('/pdfs/'):] if file.directory.find('/pdfs/') != -1 else '/pdfs/'# Udržuje vše od /pdfs/ a dál a pokud se nenajde vrati /pdfs/
        } for file in results
    ])


#=========================================================================================================
@admin_bp.route('/prohlizet')
def prohlizet():
    return render_template('prohlizet.html')

@admin_bp.route('/intra')
def intra():
    return render_template('intra.html')

@admin_bp.route('/o_projektu')
def o_projektu():
    return render_template('o_projektu.html')

#===================================================================================#
# 2.3 Testovani - pri nepouzvani ZAKOMENTOVAT
@admin_bp.route('/base_inside') # za prefixem BP vratit primo stranku /dashboard..html
def base():
    return render_template('base_inside.html')

# 2.3 Testovani - pri nepouzvani ZAKOMENTOVAT
#===================================================================================#
@admin_bp.route('/test_base') # testovaci BP pro testovani novych funkcnosti pred adopci do maker!
def test_base():
    return render_template('base_admin.html')

#===================================================================================#