from flask import Blueprint, render_template, request, redirect, url_for, flash ,session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from models.models import EmployeeUser
 # A wrapper class you’ll create
from app_init import db
from sqlalchemy import text
from flask_login import login_user


auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = db.session.execute(
            text("SELECT * FROM Employee WHERE Username = :username"),
            {"username": username}
        )

        # Convert to dict-like row using `mappings()`
        user = result.mappings().first()

        if user:
            print("User found:", user)  # Optional for debug
            if user['Password'] == password:
                user_obj = EmployeeUser(user)  # Wrap the result in your user class
                login_user(user_obj)

                session['employee_id'] = user['EmployeeID']
                session['employee_name'] = user['Name']
                session['employee_type'] = user['Type']
                flash("Login successful!", "success")
                return redirect(url_for('ui_bp.add_brand'))
            else:
                flash("Incorrect password", "danger")
        else:
            flash("User not found", "danger")

    return render_template("login.html")


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth_bp.login'))
