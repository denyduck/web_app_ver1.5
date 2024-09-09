from flask import Flask

# inicializace Flask
def create_app():
    app = Flask(__name__, instance_relative_config=False, static_folder='../static')
    app.config.from_object("config.Config")


    # importuj hlavni BP routes
    from app.routes import routes_bp
    # zaregistruj hlavni BP routes
    app.register_blueprint(routes_bp)


    return app
