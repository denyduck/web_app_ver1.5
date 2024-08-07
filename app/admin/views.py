from app.admin import admin_bp
from flask import render_template


@admin_bp.route('/')
def home():
    return render_template('dashboard_admin.html')