'''
REGISTRUJ STRANKY DO BP USERS
1. IMPORTY zavyslosti
2. REGISTRACE potřebnych <page>.html do obsahu blueprintu
    2.1 base_users - rozlozeni, navrh pro odvozeni maker
'''

# 1. IMPORTY
from flask import render_template
from app.routes.users import users_bp

# 2. REGISTRACE
# 2.1 base
@users_bp.route('/') # za prefixem BP vratit rovnou base
def base_users():
    return render_template('base_users.html')