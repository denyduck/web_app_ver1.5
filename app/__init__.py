from flask import Flask
from shared_models import db, migrate



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



    # Inicializace db a migrací s aplikací
    db.init_app(app)  # Inicializace databáze
    migrate.init_app(app, db)  # Inicializace migrací




    # Provedení v kontextu aplikace
    with app.app_context():
        db.create_all()

    return app



