from flask import Blueprint, render_template
from flask_login import login_required


ui_bp = Blueprint('ui_bp', __name__)
@ui_bp.route('/add-brand', methods=['GET'])
@login_required
def add_brand():
    return render_template('add_brand.html')
