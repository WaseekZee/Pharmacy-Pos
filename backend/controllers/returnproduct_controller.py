from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from app_init import db
from datetime import datetime

returnproduct_bp = Blueprint('returnproduct_bp', __name__, url_prefix='/returns')

# View returns
@returnproduct_bp.route('/')
def view_returns():
    returns = db.session.execute(text("""
        SELECT 
            r.CRID, 
            r.Date, 
            r.Quantity, 
            r.Reason,
            r.CustomerID, 
            c.Name AS CustomerName,
            r.ProductID, 
            p.ProductName,
            r.StockID
        FROM returnproduct r
        JOIN customer c ON r.CustomerID = c.CustomerID
        JOIN product p ON r.ProductID = p.ProductID
        ORDER BY r.Date DESC
    """)).fetchall()

    return render_template('view_returns.html', returns=returns, active_page='return')



# Add return - step 1: enter OrderID
@returnproduct_bp.route('/add', methods=['GET', 'POST'])
def add_return():
    if request.method == 'POST':
        order_id = request.form.get('order_id')

        if not order_id:
            flash("Please enter a valid Order ID", "danger")
            return redirect(url_for('returnproduct_bp.add_return'))

        # Fetch products from pack table related to the order
        products = db.session.execute(text("""
            SELECT pk.ProductID, pk.StockID, pk.Quantity, p.ProductName, co.CustomerID
            FROM pack pk
            JOIN product p ON pk.ProductID = p.ProductID
            JOIN customerorder co ON pk.OrderID = co.OrderID
            WHERE pk.OrderID = :order_id
        """), {'order_id': order_id}).fetchall()

        if not products:
            flash("No products found for this order.", "warning")
            return redirect(url_for('returnproduct_bp.add_return'))

        return render_template('add_return.html', products=products, order_id=order_id)

    return render_template('add_return.html', active_page='return')

# Handle submission of selected return products
@returnproduct_bp.route('/submit', methods=['POST'])
def submit_return():
    selected = request.form.getlist('return_items')

    if not selected:
        flash("You must select at least one product to return.", "danger")
        return redirect(url_for('returnproduct_bp.add_return'))

    for item in selected:
        product_id, stock_id = item.split('-')
        quantity_str = request.form.get(f'qty_{product_id}_{stock_id}')
        reason = request.form.get(f'reason_{product_id}_{stock_id}')
        customer_id = request.form.get(f'cust_{product_id}_{stock_id}')

        # Quantity validation
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                flash("Return quantity must be greater than 0.", "danger")
                return redirect(url_for('returnproduct_bp.add_return'))
        except ValueError:
            flash("Invalid quantity entered.", "danger")
            return redirect(url_for('returnproduct_bp.add_return'))

        # Get original pack quantity
        pack = db.session.execute(text("""
            SELECT Quantity FROM pack
            WHERE ProductID = :pid AND StockID = :sid
            LIMIT 1
        """), {'pid': product_id, 'sid': stock_id}).fetchone()

        if not pack:
            flash("Original pack record not found for validation.", "danger")
            return redirect(url_for('returnproduct_bp.add_return'))

        pack_qty = pack[0]

        if quantity > pack_qty:
            flash(f"Cannot return more than {pack_qty} for product ID {product_id}.", "danger")
            return redirect(url_for('returnproduct_bp.add_return'))

        # 1. Insert into returnproduct
        db.session.execute(text("""
            INSERT INTO returnproduct (Date, Quantity, Reason, CustomerID, ProductID, StockID)
            VALUES (:date, :qty, :reason, :cust_id, :pid, :sid)
        """), {
            'date': datetime.today().date(),
            'qty': quantity,
            'reason': reason,
            'cust_id': customer_id,
            'pid': product_id,
            'sid': stock_id
        })

        # 2. Restock if reason is "Change of Mind"
        if reason.strip().lower() == "change of mind":
            db.session.execute(text("""
                UPDATE stock
                SET Quantity = Quantity + :qty
                WHERE StockID = :sid AND ProductID = :pid
            """), {
                'qty': quantity,
                'sid': stock_id,
                'pid': product_id
            })

        # 3. Update or delete from pack
        if quantity == pack_qty:
            db.session.execute(text("""
                DELETE FROM pack
                WHERE ProductID = :pid AND StockID = :sid
                LIMIT 1
            """), {'pid': product_id, 'sid': stock_id})
        else:
            db.session.execute(text("""
                UPDATE pack
                SET Quantity = Quantity - :qty
                WHERE ProductID = :pid AND StockID = :sid
            """), {'qty': quantity, 'pid': product_id, 'sid': stock_id})

    db.session.commit()
    flash("Return submitted successfully!", "success")
    return redirect(url_for('returnproduct_bp.view_returns'))

