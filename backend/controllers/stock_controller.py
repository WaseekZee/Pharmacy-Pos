from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import text
from app_init import db

stock_bp = Blueprint('stock_bp', __name__, url_prefix='/stock')

# ------------------ VIEW STOCK ------------------
@stock_bp.route('/')
@login_required
def view_stock():
    from datetime import date

    # Step 1: Fetch all stock records
    stocks = db.session.execute(text("""
        SELECT s.StockID, s.ProductID, s.ExpDate , s.MfgDate,
               s.PurchasePrice, s.SellingPrice, s.Quantity,
               s.SupplierID, s.Status, p.ProductName
        FROM stock s
        JOIN product p ON s.ProductID = p.ProductID
        ORDER BY s.StockID DESC
    """)).fetchall()

    # Step 2: Evaluate status for each record and update if needed
    today = date.today()
    for stock in stocks:
        if stock.ExpDate < today:
            new_status = "Expired"
        elif stock.Quantity == 0:
            new_status = "OutOfStock"
        else:
            new_status = "Active"

        if stock.Status != new_status:
            db.session.execute(text("""
                UPDATE stock
                SET Status = :status
                WHERE StockID = :stock_id AND ProductID = :product_id
            """), {
                'status': new_status,
                'stock_id': stock.StockID,
                'product_id': stock.ProductID
            })

    db.session.commit()

    # Step 3: Re-fetch updated records to pass to template
    updated_stocks = db.session.execute(text("""
        SELECT s.StockID, s.ProductID, s.ExpDate , s.MfgDate,
               s.PurchasePrice, s.SellingPrice, s.Quantity,
               s.SupplierID, s.Status, p.ProductName
        FROM stock s
        JOIN product p ON s.ProductID = p.ProductID
        ORDER BY s.StockID DESC
    """)).fetchall()

    return render_template('view_stock.html', stocks=updated_stocks, active_page='stock')


# ------------------ ADD STOCK ------------------
@stock_bp.route('/add', methods=['POST'])
@login_required
def add_stock():
    try:
        data = {
            'stock_id': request.form['stock_id'],
            'product_id': request.form['product_id'],
            'exp_date': request.form['exp_date'],
            'mfg_date': request.form['mfg_date'],
            'purchase_price': request.form['purchase_price'],
            'selling_price': request.form['selling_price'],
            'quantity': request.form['quantity'],
            'supplier_id': request.form['supplier_id']
        }

        db.session.execute(text("""
            INSERT INTO stock (StockID, ProductID, ExpDate, MfgDate,
                               PurchasePrice, SellingPrice, Quantity, SupplierID)
            VALUES (:stock_id, :product_id, :exp_date, :mfg_date,
                    :purchase_price, :selling_price, :quantity, :supplier_id)
        """), data)

        db.session.commit()
        flash("Stock added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding stock: {e}", "danger")
    
    return redirect(url_for('stock_bp.view_stock'))

# ------------------ UPDATE STOCK ------------------
@stock_bp.route('/update', methods=['POST'])
@login_required
def update_stock():
    data = request.get_json()
    stock_id = data.get('stock_id')
    product_id = data.get('product_id')
    new_quantity = data.get('quantity')
    new_price = data.get('selling_price')

    try:
        db.session.execute(text("""
            UPDATE Stock
            SET Quantity = :quantity, SellingPrice = :selling_price
            WHERE StockID = :stock_id AND ProductID = :product_id
        """), {
            'stock_id': stock_id,
            'product_id': product_id,
            'quantity': new_quantity,
            'selling_price': new_price
        })
        db.session.commit()
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}


# ------------------ DELETE STOCK ------------------
@stock_bp.route('/delete/<int:stock_id>/<int:product_id>', methods=['POST'])
@login_required
def delete_stock(stock_id, product_id):
    try:
        db.session.execute(text("""
            DELETE FROM stock WHERE StockID = :stock_id AND ProductID = :product_id
        """), {'stock_id': stock_id, 'product_id': product_id})
        db.session.commit()
        flash("Stock deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting stock: {e}", "danger")

    return redirect(url_for('stock_bp.view_stock'))
