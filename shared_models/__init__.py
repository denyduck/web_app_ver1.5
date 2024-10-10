from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine  # Opravený import
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker


#==========================================================================
# RABBITMQ SQLAlchemy
#==========================================================================


# Připojení k MySQL
DATABASE_URI = 'mysql+pymysql://root:root_password@db/my_database'
engine = create_engine(DATABASE_URI)

# Vytvoření základní třídy pro ORM
Base = declarative_base()

# Vytvoření session
Session = sessionmaker(bind=engine)
session = Session()

#==========================================================================
# FLASK
#==========================================================================
# Inicializace FLASK-SQLAlchemy
db = SQLAlchemy()

# Inicializace správy migraci pro databaze
migrate = Migrate()





from shared_models import rabbit_models