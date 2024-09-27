from flask_sqlalchemy import SQLAlchemy

# Inicializace SQLAlchemy
db = SQLAlchemy()


# Import všech modelů
from .pdf_models import Pdflist