'''
REGISTRUJ STRANKY DO BP USERS
1. IMPORTY zavyslosti
2. REGISTRACE potřebnych <page>.html do obsahu blueprintu
    2.1 base_users - rozlozeni, navrh pro odvozeni maker
'''

# 1. IMPORTY
import requests
from app.routes.requests import file_changes
from flask import Flask, request

# 2. REGISTRACE
# 2.1 base
@file_changes.route('/file_dog', methods=['POST']) # za prefixem BP vratit rovnou base
def file_changed():
    data = request.get_json()
    file_path = data.get('file')

    print(f'Soubor změněn: {file_path}')

    # zde provest akce s databází!