from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from sqlalchemy import text
from app_init import db

order_bp = Blueprint('order_bp', __name__, url_prefix='/orders')

# ------------------ ADD ORDER ------------------
@order_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_order():
    if request.method == 'POST':
        date = request.form['date']
        quantity = request.form['quantity']
        total_amount = request.form['total_amount']
        payment_type = request.form['payment_type']
        customer_id = request.form['customer_id']
        employee_id = session.get('employee_id')

        try:
            db.session.execute(text("""
                INSERT INTO customerorder (Date, Quantity, TotalAmount, PaymentType, CustomerID, EmployeeID)
                VALUES (:date, :quantity, :total_amount, :payment_type, :customer_id, :employee_id)
            """), {
                'date': date,
                'quantity': quantity,
                'total_amount': total_amount,
                'payment_type': payment_type,
                'customer_id': customer_id,
                'employee_id': employee_id
            })
            db.session.commit()
            flash("Order placed successfully!", "success")
            return redirect(url_for('order_bp.view_orders'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error placing order: {e}", "danger")

    customers = db.session.execute(text("SELECT CustomerID, Name, Phone FROM Customer")).fetchall()
    return render_template("add_order.html", customers=customers)

# ------------------ VIEW ORDERS ------------------
@order_bp.route('/view', methods=['GET'])
@login_required
def view_orders():
    orders = db.session.execute(text("""
        SELECT o.OrderID, o.Date, o.Quantity, o.TotalAmount, o.PaymentType,
               c.Name AS CustomerName, e.Name AS EmployeeName
        FROM customerorder o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        JOIN Employee e ON o.EmployeeID = e.EmployeeID
    """)).fetchall()
    return render_template("view_orders.html", orders=orders)

# ------------------ DELETE ORDER ------------------
@order_bp.route('/delete/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    try:
        db.session.execute(text("DELETE FROM customerorder WHERE OrderID = :id"), {'id': order_id})
        db.session.commit()
        flash("Order deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting order: {e}", "danger")

    return redirect(url_for('order_bp.view_orders'))

# ------------------ EDIT ORDER ------------------
@order_bp.route('/edit/<int:order_id>', methods=['POST'])
@login_required
def edit_order(order_id):
    new_date = request.form['editDate']
    new_quantity = request.form['editQuantity']
    new_total = request.form['editTotalAmount']
    new_payment = request.form['editPaymentType']
    new_customer_id = request.form['editCustomerID']

    try:
        db.session.execute(text("""
            UPDATE customerorder
            SET Date = :date,
                Quantity = :quantity,
                TotalAmount = :total,
                PaymentType = :payment,
                CustomerID = :customer_id
            WHERE OrderID = :id
        """), {
            'date': new_date,
            'quantity': new_quantity,
            'total': new_total,
            'payment': new_payment,
            'customer_id': new_customer_id,
            'id': order_id
        })
        db.session.commit()
        flash("Order updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating order: {e}", "danger")

    return redirect(url_for('order_bp.view_orders'))


@order_bp.route('/add_customer', methods=['POST'])
def add_customer_ajax():
    name = request.form.get('name')
    phone = request.form.get('phone')

    try:
        db.session.execute(text("""
            INSERT INTO Customer (Name, Phone)
            VALUES (:name, :phone)
        """), {'name': name, 'phone': phone})
        db.session.commit()

        new_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        return {"success": True, "customer_id": new_id, "name": name}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}

