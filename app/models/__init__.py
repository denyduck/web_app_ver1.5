from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicializace SQLAlchemy
db = SQLAlchemy()
# Inicializace správy migraci pro databaze
migrate = Migrate()

# Import všech modelů
from .pdf_models import Pdflist