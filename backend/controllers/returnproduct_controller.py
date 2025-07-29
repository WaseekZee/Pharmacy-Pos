from flask import Blueprint, render_template, request, redirect, url_for, flash , session
from sqlalchemy import text
from app_init import db
from datetime import datetime

returnproduct_bp = Blueprint('returnproduct_bp', __name__, url_prefix='/returns')

# View returns
@returnproduct_bp.route('/')
def view_returns():
    # Get current page number
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # Get total number of return invoices
    total_count = db.session.execute(text("SELECT COUNT(*) FROM returninvoice")).scalar()
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division

    # Fetch paginated return invoices
    invoices = db.session.execute(text("""
        SELECT ri.InvoiceID, ri.Date, ri.Amount,
               c.Name AS CustomerName,
               e.Name AS EmployeeName
        FROM returninvoice ri
        JOIN customer c ON ri.CustomerID = c.CustomerID
        JOIN employee e ON ri.EmployeeID = e.EmployeeID
        ORDER BY ri.Date DESC
        LIMIT :limit OFFSET :offset
    """), {"limit": per_page, "offset": offset}).fetchall()

    return render_template('view_returns.html',
                           invoices=invoices,
                           page=page,
                           total_pages=total_pages,
                           active_page='return')




# Add return - step 1: enter OrderID
@returnproduct_bp.route('/add', methods=['GET', 'POST'])
def add_return():
    if request.method == 'POST':
        order_id = request.form.get('order_id')

        if not order_id:
            flash("Please enter a valid Order ID", "danger")
            return redirect(url_for('returnproduct_bp.add_return'))

        # Check if this order has already been returned
        existing_return = db.session.execute(text("""
            SELECT 1 FROM returninvoice WHERE OrderID = :order_id LIMIT 1
        """), {'order_id': order_id}).scalar()

        if existing_return:
            # If the order has already been returned, show a flash message and prevent further return
            flash("This order has already been returned. You cannot return the products again.", "warning")
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

        return render_template('add_return.html', products=products, order_id=order_id , active_page='return')

    return render_template('add_return.html', active_page='return')


@returnproduct_bp.route('/invoice/<int:invoice_id>')
def view_invoice(invoice_id):
    # Get invoice summary
    invoice = db.session.execute(text("""
        SELECT ri.*, c.Name AS CustomerName, e.Name AS EmployeeName
        FROM returninvoice ri
        JOIN customer c ON ri.CustomerID = c.CustomerID
        JOIN employee e ON ri.EmployeeID = e.EmployeeID
        WHERE ri.InvoiceID = :iid
    """), {'iid': invoice_id}).fetchone()

    # Get all return products linked to this invoice
    products = db.session.execute(text("""
        SELECT r.*, p.ProductName
        FROM returnproduct r
        JOIN product p ON r.ProductID = p.ProductID
        WHERE r.InvoiceID = :iid
    """), {'iid': invoice_id}).fetchall()

    return render_template('view_invoice.html', invoice=invoice, products=products , active_page='return')


# Handle submission of selected return products
from sqlalchemy import text
from datetime import datetime
from flask import request, redirect, url_for, flash, session
from app_init import db

@returnproduct_bp.route('/submit', methods=['POST'])
def submit_return():
    selected = request.form.getlist('return_items')
    reasons = request.form
    order_id = request.form.get('order_id')
    employee_id = session.get('employee_id')  # assuming employee ID is stored in session

    if not selected:
        flash("Please select at least one product to return.", "warning")
        return redirect(url_for('returnproduct_bp.add_return'))

    total_amount = 0
    crids = []

    for item in selected:
        product_id, stock_id = item.split('-')
        quantity = int(request.form.get(f'qty_{product_id}_{stock_id}'))
        reason = request.form.get(f'reason_{product_id}_{stock_id}')
        customer_id = request.form.get(f'cust_{product_id}_{stock_id}')
        price = float(request.form.get(f'price_{product_id}_{stock_id}'))

        # Business logic for "Changed mind"
        if reason in ["Changed mind", "Expired"]:
            db.session.execute(text("""
                UPDATE stock
                SET Quantity = Quantity + :qty
                WHERE ProductID = :pid AND StockID = :sid
            """), {'qty': quantity, 'pid': product_id, 'sid': stock_id})

        elif reason == "Defective":
            db.session.execute(text("""
                UPDATE stock
                SET Damaged = Damaged + :qty
                WHERE ProductID = :pid AND StockID = :sid
            """), {'qty': quantity, 'pid': product_id, 'sid': stock_id})

        original_qty = db.session.execute(text("""
            SELECT Quantity FROM pack
            WHERE ProductID = :pid AND StockID = :sid AND OrderID = :oid
        """), {'pid': product_id, 'sid': stock_id, 'oid': order_id}).scalar()

        if not original_qty or quantity > original_qty:
            flash(f"Cannot return more than originally purchased for product ID {product_id}.", "danger")
            return redirect(url_for('returnproduct_bp.add_return'))
        
        # Insert into returnproduct first (invoice ID is placeholder for now)
        result = db.session.execute(text("""
            INSERT INTO returnproduct 
                (Date, Quantity, Reason, CustomerID, ProductID, StockID, OrderID, InvoiceID) 
            VALUES 
                (:date, :qty, :reason, :cust_id, :pid, :sid, :oid, NULL)
        """), {
            'date': datetime.today().date(),
            'qty': quantity,
            'reason': reason,
            'cust_id': customer_id,
            'pid': product_id,
            'sid': stock_id,
            'oid': order_id
        })

        # Get CRID of inserted returnproduct
        crid = db.session.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        crids.append(crid)

        # Add subtotal
        total_amount += quantity * price

    # Insert single invoice record
    customer_id = request.form.get(f'cust_{selected[0].split("-")[0]}_{selected[0].split("-")[1]}')
    db.session.execute(text("""
        INSERT INTO returninvoice (CustomerID, EmployeeID, Date, Amount , OrderID)
        VALUES (:cust_id, :emp_id, :date, :amount , :oid)
    """), {
        'cust_id': customer_id,
        'emp_id': employee_id,
        'date': datetime.today().date(),
        'amount': total_amount,
        'oid': order_id
    })

    # Get new InvoiceID
    invoice_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).scalar()

    # Update returnproduct rows with InvoiceID
    for crid in crids:
        db.session.execute(text("""
            UPDATE returnproduct 
            SET InvoiceID = :invoice_id 
            WHERE CRID = :crid
        """), {'invoice_id': invoice_id, 'crid': crid})

    db.session.commit()
    flash("Return processed and invoice created successfully.", "success")
    return redirect(url_for('returnproduct_bp.view_returns'))
