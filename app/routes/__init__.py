from flask import Blueprint

# vytvoření hlavniho BP pro registrace stranek html ve views
routes_bp = Blueprint('routes', __name__)


# imporuj BP z jednotlivych podmodulu
from app.routes.admin import admin_bp
from app.routes.users import users_bp

# importovane BP zaregistruj do hlavniho BP routes
routes_bp.register_blueprint(admin_bp)
routes_bp.register_blueprint(users_bp)

# po registraci BP nacti cesty html souboru z views
from app.routes.admin import views
from app.routes.users import views




