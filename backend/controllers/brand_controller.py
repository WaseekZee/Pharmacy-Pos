from flask import Blueprint, render_template, request, redirect, url_for , flash
from app_init import db
from sqlalchemy import text
from flask_login import login_required


brand_bp = Blueprint('brand_bp', __name__, url_prefix='/brands')
@brand_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_brand():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description')

        try:
            db.session.execute(
                text("INSERT INTO Brand (name, description) VALUES (:name, :description)"),
                {"name": name, "description": description}
            )
            db.session.commit()
            flash('Brand added successfully!', 'success')
            return redirect(url_for('brand_bp.add_brand'))
        except Exception as e:
            return f"Error adding brand: {e}"

    return render_template('add_brand.html')

