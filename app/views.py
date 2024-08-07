from flask import Blueprint, render_template

my_bp = Blueprint('my', __name__, template_folder='templates')

@my_bp.route('/')
def home():
    ukaz = render_template('dashboard_admin.html')
    print(ukaz)
    return ukaz