from flask import Blueprint

# vytvoření BP pro registrace stranek html ve views
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# po registraci BP načíst cesty html soubrů z views (pro oddělení views a reg.BP)
from app.admin import views