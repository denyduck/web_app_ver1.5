from flask import Flask

# inicializace Flask
def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")



    from app.admin import admin_bp
    app.register_blueprint(admin_bp)


 #   with app.app_context():
       # from app.routes import main_bp

        # Import Dash Aplikace
        #from .plytlydash.dashboard import create_dashboard

    return app
