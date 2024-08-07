from app.admin import admin_bp
from flask import render_template


# API - registrace jednotlivých page.html do BP admin_bp
@admin_bp.route('/')
def home():
    return render_template('dashboard_admin.html')