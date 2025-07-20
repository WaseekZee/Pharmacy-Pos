from flask import Blueprint, render_template, request, redirect, url_for, flash , session
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
            r.StockID,
            r.OrderID                          
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
        # Updated pack query to include SellingPrice
        products = db.session.execute(text("""
            SELECT pk.ProductID, pk.StockID, pk.Quantity, p.ProductName, co.CustomerID, s.SellingPrice
            FROM pack pk
            JOIN product p ON pk.ProductID = p.ProductID
            JOIN customerorder co ON pk.OrderID = co.OrderID
            JOIN stock s ON pk.StockID = s.StockID AND pk.ProductID = s.ProductID
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
    reasons = request.form
    order_id = request.form.get('order_id')  # Add this line

    if not selected:
        flash("Please select at least one product to return.", "danger")
        return redirect(url_for('returnproduct_bp.add_return'))

    for item in selected:
        product_id, stock_id = item.split('-')
        quantity = request.form.get(f'qty_{product_id}_{stock_id}')
        reason = request.form.get(f'reason_{product_id}_{stock_id}')
        customer_id = request.form.get(f'cust_{product_id}_{stock_id}')

        # Get price from database for safety
        price_row = db.session.execute(text("""
            SELECT SellingPrice FROM stock WHERE ProductID = :pid AND StockID = :sid
        """), {'pid': product_id, 'sid': stock_id}).fetchone()
    
        quantity = int(request.form.get(f'qty_{product_id}_{stock_id}'))
        price = float(request.form.get(f'price_{product_id}_{stock_id}'))
        subtotal = quantity * price
        #total_amount += subtotal

        # Optional: Validate quantity not exceeding originally purchased
        original_qty = db.session.execute(text("""
            SELECT Quantity FROM pack
            WHERE ProductID = :pid AND StockID = :sid AND OrderID = :oid
        """), {'pid': product_id, 'sid': stock_id, 'oid': order_id}).scalar()

        if not original_qty or int(quantity) > original_qty:
            flash(f"Cannot return more than originally purchased for product ID {product_id}.", "danger")
            return redirect(url_for('returnproduct_bp.add_return'))

        db.session.execute(text("""
            INSERT INTO returnproduct (Date, Quantity, Reason, CustomerID, ProductID, StockID, OrderID)
            VALUES (:date, :qty, :reason, :cust_id, :pid, :sid, :oid)
        """), {
            'date': datetime.today().date(),
            'qty': quantity,
            'reason': reason,
            'cust_id': customer_id,
            'pid': product_id,
            'sid': stock_id,
            'oid': order_id
        })

        crid = db.session.execute(text("SELECT LAST_INSERT_ID()")).scalar()

        # Insert into returninvoice
        db.session.execute(text("""
            INSERT INTO returninvoice (CRID, CustomerID, EmployeeID, Date, Amount)
            VALUES (:crid, :cust_id, :emp_id, :date, :amount)
        """), {
            'crid': crid,
            'cust_id': customer_id,
            'emp_id': session.get('employee_id'),  # Assume employee ID is stored in session
            'date': datetime.today().date(),
            'amount': subtotal  # You must calculate this
        })

        # If reason is "Changed mind" → restock it
        if reason in ["Changed mind", "Expired"]:
            db.session.execute(text("""
                UPDATE stock
                SET Quantity = Quantity + :qty
                WHERE ProductID = :pid AND StockID = :sid
            """), {'qty': quantity, 'pid': product_id, 'sid': stock_id})

        elif reason == "Defective item":
         # Increase damaged count
            db.session.execute(text("""
                UPDATE stock
                SET Damaged = Damaged + :qty
                WHERE ProductID = :pid AND StockID = :sid
            """), {'qty': quantity, 'pid': product_id, 'sid': stock_id})


        # If full quantity returned, delete from `pack`


    db.session.commit()
    flash("Return submitted successfully!", "success")
    return redirect(url_for('returnproduct_bp.view_returns'))

