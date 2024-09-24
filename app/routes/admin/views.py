'''
REGISTRUJ STRANKY DO BP ADMIN
1. IMPORTY zavyslosti
2. REGISTRACE potřebnych <page>.html do obsahu blueprintu
    2.1 base_admin - rozlozeni, navrh pro odvozeni maker
    2.2 home
    2.3 *Testování BASE pred nasazením

'''

# 1. IMPORTY
from flask import render_template
from app.routes.admin import admin_bp



# 2. REGISTRACE

@admin_bp.route('/')
def home():

    return render_template('home.html')

@admin_bp.route('/prohlizet')
def prohlizet():
    return render_template('prohlizet.html')







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