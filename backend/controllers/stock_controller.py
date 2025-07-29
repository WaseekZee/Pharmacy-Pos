from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import text
from app_init import db

stock_bp = Blueprint('stock_bp', __name__, url_prefix='/stock')


@stock_bp.route('/')
@login_required
def view_stock():
    from datetime import date

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # Step 1: Update statuses globally (for simplicity)
    stocks_to_update = db.session.execute(text("""
        SELECT StockID, ProductID, ExpDate, Quantity, Status
        FROM stock
    """)).fetchall()

    today = date.today()
    for stock in stocks_to_update:
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

    # Step 2: Get total count for pagination
    total_count = db.session.execute(text("SELECT COUNT(*) FROM stock")).scalar()
    total_pages = (total_count + per_page - 1) // per_page

    # Step 3: Fetch paginated stock records
    paginated_stocks = db.session.execute(text("""
        SELECT s.StockID, s.ProductID, s.ExpDate , s.MfgDate,
               s.PurchasePrice, s.SellingPrice, s.Quantity,
               s.SupplierID, s.Status, s.Damaged, p.ProductName
        FROM stock s
        JOIN product p ON s.ProductID = p.ProductID
        ORDER BY s.StockID DESC
        LIMIT :limit OFFSET :offset
    """), {"limit": per_page, "offset": offset}).fetchall()

    return render_template('view_stock.html',
                           stocks=paginated_stocks,
                           page=page,
                           total_pages=total_pages,
                           active_page='stock')


@stock_bp.route('/add', methods=['GET'])
@login_required
def add_stock():
    products = db.session.execute(text("SELECT ProductID, ProductName FROM product")).fetchall()
    suppliers = db.session.execute(text("SELECT SupplierID, Name FROM supplier")).fetchall()
    return render_template('add_stock.html', products=products, suppliers=suppliers, active_page='stock')


# ------------------ ADD STOCK ------------------
@stock_bp.route('/add', methods=['POST'])
@login_required
def add_stock_post():
    from datetime import date
    form = request.form

    supplier_id = form.get('supplier_id')
    total_items = int(form.get('total_items'))

    try:
        # Generate a new StockID by getting max and adding 1 (or use sequence if DB supports)
        stock_id_result = db.session.execute(text("SELECT COALESCE(MAX(StockID), 0) + 1 AS NewStockID FROM stock"))
        stock_id = stock_id_result.fetchone().NewStockID

        for i in range(1, total_items + 1):
            product_id = form.get(f'product_id_{i}')
            exp_date = form.get(f'exp_date_{i}')
            mfg_date = form.get(f'mfg_date_{i}')
            purchase_price = form.get(f'purchase_price_{i}')
            selling_price = form.get(f'selling_price_{i}')
            quantity = int(form.get(f'quantity_{i}'))

            # Determine status
            status = 'Active'
            if exp_date and date.fromisoformat(exp_date) < date.today():
                status = 'Expired'
            elif quantity == 0:
                status = 'OutOfStock'

            db.session.execute(text("""
                INSERT INTO stock (
                    StockID, ProductID, ExpDate, MfgDate,
                    PurchasePrice, SellingPrice, Quantity,
                    SupplierID, Status
                )
                VALUES (
                    :stock_id, :product_id, :exp_date, :mfg_date,
                    :purchase_price, :selling_price, :quantity,
                    :supplier_id, :status
                )
            """), {
                'stock_id': stock_id,
                'product_id': product_id,
                'exp_date': exp_date,
                'mfg_date': mfg_date,
                'purchase_price': purchase_price,
                'selling_price': selling_price,
                'quantity': quantity,
                'supplier_id': supplier_id,
                'status': status
            })

        db.session.commit()
        flash('Stock items added successfully!', 'success')
        return redirect(url_for('stock_bp.view_stock'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding stock: {e}', 'danger')
        return redirect(url_for('stock_bp.add_stock'))



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
