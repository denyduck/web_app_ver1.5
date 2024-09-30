from flask import Blueprint

file_changes = Blueprint('file_changes', __name__, template_folder='templates', url_prefix='/requests')
