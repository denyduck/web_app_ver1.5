from flask import Flask
from app.models import db, Pdflist
#from config import get_config
# inicializace Flask
def create_app():
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object("config.Config")

    #config = get_config()
    #app.config.from_object(config)

    # importuj hlavni BP routes
    from app.routes import routes_bp
    # zaregistruj hlavni BP routes
    app.register_blueprint(routes_bp)



    db.init_app(app)

    # Provedení v kontextu aplikace
    with app.app_context():
        db.create_all()

    return app



'''    # zajištění propojení do kontextu aplikace:
    with app.app_context():
        # vytvoří všechny tabulky
        db.create_all()'''




