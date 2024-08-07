from flask import Flask

# inicializace Flask
def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")


    # import BP pro jeho registraci
    from app.admin import admin_bp
    # registrace BP
    app.register_blueprint(admin_bp)


    return app
