from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#==========================================================================
# RABBITMQ
#==========================================================================
Base = declarative_base()



#==========================================================================
# FLASK
#==========================================================================
# Inicializace SQLAlchemy
db = SQLAlchemy()

# Inicializace správy migraci pro databaze
migrate = Migrate()
