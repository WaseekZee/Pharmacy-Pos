from flask import Blueprint, render_template

ui_bp = Blueprint('ui_bp', __name__)

@ui_bp.route('/add-brand', methods=['GET'])
def add_brand():
    return render_template('add_brand.html')
