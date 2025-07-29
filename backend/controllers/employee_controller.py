from flask import Blueprint, render_template, request, redirect, url_for, flash
from app_init import db
from sqlalchemy import text
from flask_login import login_required

employee_bp = Blueprint('employee_bp', __name__, url_prefix='/employees')


# ------------------ Add Employee ------------------
@employee_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        emp_type = request.form['type']
        password = request.form['password']
        username = request.form['username']

        try:
            db.session.execute(
                text("""
                    INSERT INTO Employee (Name, Type, Password, Username)
                    VALUES (:name, :type, :password, :username)
                """),
                {
                    "name": name,
                    "type": emp_type,
                    "password": password,
                    "username": username
                }
            )
            db.session.commit()

            flash("Employee added successfully!", "success")  # ✅ set the flash message
            return redirect(url_for('employee_bp.view_employees'))  # ✅ correct redirect target

        except Exception as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('employee_bp.add_employee'))

    return render_template("add_employee.html", active_page="employee")


# ------------------ View Employees ------------------
@employee_bp.route('/view', methods=['GET'])
@login_required
def view_employees():
    employees = db.session.execute(text("SELECT * FROM Employee")).fetchall()
    return render_template("view_employees.html", employees=employees, active_page="employee")


# ------------------ Edit Employee ------------------
@employee_bp.route('/edit/<int:employee_id>', methods=['POST'])
@login_required
def edit_employee(employee_id):
    name = request.form['editName']
    emp_type = request.form['editType']
    password = request.form['editPassword']
    username = request.form['editUsername']

    try:
        db.session.execute(
            text("""
                UPDATE Employee
                SET Name = :name,
                    Type = :type,
                    Password = :password,
                    Username = :username
                WHERE EmployeeID = :id
            """),
            {
                'name': name,
                'type': emp_type,
                'password': password,
                'username': username,
                'id': employee_id
            }
        )
        db.session.commit()
        flash("Employee updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating employee: {e}", "danger")

    return redirect(url_for('employee_bp.view_employees'))


# ------------------ Delete Employee ------------------
@employee_bp.route('/delete/<int:employee_id>', methods=['POST'])
@login_required
def delete_employee(employee_id):
    try:
        db.session.execute(
            text("DELETE FROM Employee WHERE EmployeeID = :id"),
            {'id': employee_id}
        )
        db.session.commit()
        flash("Employee deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting employee: {e}", "danger")

    return redirect(url_for('employee_bp.view_employees'))
