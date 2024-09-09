'''
REGISTRUJ STRANKY DO BP ADMIN
1. IMPORTY zavyslosti
2. REGISTRACE potřebnych <page>.html do obsahu blueprintu
    2.1 base_admin - rozlozeni, navrh pro odvozeni maker
    2.2 home

'''

# 1. IMPORTY
from flask import render_template
from app.routes.admin import admin_bp


# 2. REGISTRACE
# 2.1 base
@admin_bp.route('/')
def base():
    return render_template('base_admin.html')

# 2.2 home
@admin_bp.route('home') # za prefixem BP vratit primo stranku /dashboard..html
def home():
    return render_template('home.html')


