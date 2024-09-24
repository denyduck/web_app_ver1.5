from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='templates', url_prefix='/') # pridat prefix pro oddeleni routu