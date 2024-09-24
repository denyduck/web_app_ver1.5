from flask import current_app
from app.config import Config
import os
def search_pdf():
    # vrat mi hodnotu z configu.py z PDF_DIRECTORY
    pdf_directory = current_app.config['PDF_DIRECTORY']
    print(pdf_directory)

search_pdf()