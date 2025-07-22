from flask import Blueprint, render_template, request, redirect, url_for, flash
from app_init import db
from sqlalchemy import text
from flask_login import login_required

supplier_bp = Blueprint('supplier_bp', __name__, url_prefix='/suppliers')


# ------------------ Add Supplier ------------------
@supplier_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        name = request.form['supplierName']
        telephone = request.form['telephone']
        bank_account = request.form['bankAccount']
        address = request.form['address']

        try:
            db.session.execute(
                text("""
                    INSERT INTO supplier (Name, Telephone, BankAccount, Address)
                    VALUES (:name, :telephone, :bank_account, :address)
                """),
                {
                    "name": name,
                    "telephone": telephone,
                    "bank_account": bank_account,
                    "address": address
                }
            )
            db.session.commit()
            flash('Supplier added successfully!', 'success')
            return redirect(url_for('supplier_bp.add_supplier'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
            return redirect(url_for('supplier_bp.add_supplier'))

    return render_template("add_supplier.html", active_page="supplier")


# ------------------ View Suppliers ------------------
@supplier_bp.route('/view', methods=['GET'])
@login_required
def view_suppliers():
    suppliers = db.session.execute(text("""
        SELECT * FROM supplier
    """)).fetchall()

    return render_template("view_suppliers.html", suppliers=suppliers, active_page="supplier")


# ------------------ Edit Supplier ------------------
@supplier_bp.route('/edit/<int:supplier_id>', methods=['POST'])
@login_required
def edit_supplier(supplier_id):
    new_name = request.form['editSupplierName']
    new_telephone = request.form['editTelephone']
    new_bank_account = request.form['editBankAccount']
    new_address = request.form['editAddress']

    try:
        db.session.execute(
            text("""
                UPDATE supplier
                SET Name = :name,
                    Telephone = :telephone,
                    BankAccount = :bank_account,
                    Address = :address
                WHERE SupplierID = :id
            """),
            {
                'name': new_name,
                'telephone': new_telephone,
                'bank_account': new_bank_account,
                'address': new_address,
                'id': supplier_id
            }
        )
        db.session.commit()
        flash("Supplier updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating supplier: {e}", "danger")

    return redirect(url_for('supplier_bp.view_suppliers'))


# ------------------ Delete Supplier ------------------
@supplier_bp.route('/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    try:
        db.session.execute(
            text("DELETE FROM supplier WHERE SupplierID = :id"),
            {'id': supplier_id}
        )
        db.session.commit()
        flash("Supplier deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting supplier: {e}", "danger")

    return redirect(url_for('supplier_bp.view_suppliers'))
