from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from datetime import datetime
from app_init import db  # or wherever your db instance is

supplier_return_bp = Blueprint('supplier_return_bp', __name__)

def get_stock_dropdown_data():
    """Get dropdown data for Stock IDs"""
    query = """
        SELECT DISTINCT s.StockID
        FROM stock s
        WHERE s.Status != 'Returned'
        AND NOT EXISTS (
            SELECT 1 FROM returnedstock r 
            WHERE r.StockID = s.StockID AND r.ProductID = s.ProductID
        )
        ORDER BY s.StockID
    """
    
    result = db.session.execute(text(query))
    stock_ids = [row.StockID for row in result.fetchall()]
    return stock_ids

@supplier_return_bp.route('/get_products_for_stock', methods=['GET'])
def get_products_for_stock():
    """AJAX endpoint to get products for a specific Stock ID"""
    stock_id = request.args.get('stock_id')
    
    if not stock_id:
        return {'products': []}
    
    query = """
        SELECT s.ProductID, p.ProductName
        FROM stock s
        JOIN product p ON s.ProductID = p.ProductID
        WHERE s.StockID = :stock_id
        AND s.Status != 'Returned'
        AND NOT EXISTS (
            SELECT 1 FROM returnedstock r 
            WHERE r.StockID = s.StockID AND r.ProductID = s.ProductID
        )
        ORDER BY p.ProductName
    """
    
    try:
        result = db.session.execute(text(query), {'stock_id': stock_id})
        products = [{'product_id': row.ProductID, 'product_name': row.ProductName} 
                   for row in result.fetchall()]
        return {'products': products}
    except Exception as e:
        return {'products': [], 'error': str(e)}
    """Helper function to get returns list with filtering and pagination"""
    offset = (page - 1) * per_page

    base_query = """
        SELECT 
            s.StockID, s.ProductID, s.SupplierID,
            sup.Name AS SupplierName,
            p.ProductName, s.ExpDate,
            CASE 
                WHEN s.Status = 'Expired' THEN 'Expired'
                WHEN s.Damaged > 0 THEN 'Damaged'
                ELSE 'Other'
            END AS Reason,
            CASE 
                WHEN s.Status = 'Expired' THEN s.Quantity
                WHEN s.Damaged > 0 THEN s.Damaged
                ELSE 0
            END AS ReturnQuantity
        FROM stock s
        JOIN product p ON s.ProductID = p.ProductID
        JOIN supplier sup ON s.SupplierID = sup.SupplierID
        WHERE ((s.Status = 'Expired' AND s.Quantity != 0) OR s.Damaged > 0)
        AND s.Status != 'Returned'
        AND NOT EXISTS (
            SELECT 1 FROM returnedstock r 
            WHERE r.StockID = s.StockID AND r.ProductID = s.ProductID
        )
    """

    # Final query with optional reason filter
    full_query = f"SELECT * FROM ({base_query}) AS sub"
    params = {'limit': per_page, 'offset': offset}
    
    if reason_filter != 'all':
        full_query += f" WHERE Reason = :reason"
        params['reason'] = reason_filter

    full_query += f" LIMIT :limit OFFSET :offset"

    result = db.session.execute(text(full_query), params)
    rows = result.fetchall()

    # Count query
    count_query = f"SELECT COUNT(*) as total FROM ({base_query}) AS sub"
    if reason_filter != 'all':
        count_query += " WHERE Reason = :reason"
        count_params = {'reason': reason_filter}
    else:
        count_params = {}

    total_rows = db.session.execute(text(count_query), count_params).scalar()
    total_pages = (total_rows + per_page - 1) // per_page

    return {
        'returns': rows,
        'total_pages': total_pages,
        'total_rows': total_rows
    }

@supplier_return_bp.route('/supplier_returns')
def supplier_returns():
    reason_filter = request.args.get('reason', 'all')
    page = int(request.args.get('page', 1))
    manual_cleared = request.args.get('manual_cleared')
    
    # Get the main returns data
    data = get_returns_data(reason_filter, page)
    
    # Get dropdown data for manual return section
    stock_options = get_stock_dropdown_data()
    
    # Only clear manual item if explicitly requested
    manual_item = None
    manual_message = None
    
    return render_template("supplier_returns.html", 
                         returns=data['returns'],
                         reason_filter=reason_filter,
                         current_page=page,
                         total_pages=data['total_pages'],
                         manual_item=manual_item,
                         manual_message=manual_message,
                         stock_options=stock_options)

@supplier_return_bp.route('/process_return', methods=['POST'])
def process_return():
    stock_id = request.form['stock_id']
    product_id = request.form['product_id']
    reason = request.form['reason']
    quantity = request.form['quantity']
    
    # Check if this is a manual return or from the main list
    is_manual_return = request.form.get('manual_return') == 'true'
    return_to_list = request.form.get('return_to_list') == 'true'
    
    # Preserve current Section A state
    current_reason_filter = request.form.get('current_reason_filter', 'all')
    current_page = int(request.form.get('current_page', 1))

    try:
        # Insert into returnedstock table
        db.session.execute(text("""
            INSERT INTO returnedstock (ReturnedDate, Reason, Quantity, StockID, ProductID)
            VALUES (:date, :reason, :qty, :sid, :pid)
        """), {
            'date': datetime.today(),
            'reason': reason,
            'qty': quantity,
            'sid': stock_id,
            'pid': product_id
        })

        # Update stock status
        db.session.execute(text("""
            UPDATE stock SET Status = 'Returned'
            WHERE StockID = :sid AND ProductID = :pid
        """), {
            'sid': stock_id,
            'pid': product_id
        })

        db.session.commit()
        
        if is_manual_return:
            flash("Manual return processed successfully.", "success")
            # For manual returns, clear the manual item but preserve Section A filters
            return redirect(url_for('supplier_return_bp.supplier_returns', 
                                  reason=current_reason_filter, 
                                  page=current_page,
                                  manual_cleared='true'))
        else:
            flash("Return processed successfully.", "success")
            # For list returns, just preserve the current state
            return redirect(url_for('supplier_return_bp.supplier_returns', 
                                  reason=current_reason_filter, 
                                  page=current_page))
            
    except Exception as e:
        db.session.rollback()
        flash(f"Error processing return: {str(e)}", "error")
        return redirect(url_for('supplier_return_bp.supplier_returns', 
                              reason=current_reason_filter, 
                              page=current_page))

@supplier_return_bp.route('/manual_return_lookup', methods=['POST'])  # Fixed route name
def manual_return_lookup():
    stock_id = request.form.get('stock_id')
    product_id = request.form.get('product_id')
    
    # Preserve Section A state
    current_reason_filter = request.form.get('current_reason_filter', 'all')
    current_page = int(request.form.get('current_page', 1))
    
    # Get the main returns data (Section A) - this should NOT be affected
    data = get_returns_data(current_reason_filter, current_page)

    # Lookup manual item (Section B)
    manual_item = None
    manual_message = None
    
    if stock_id and product_id:
        # Fetch the item details (without restrictions)
        check_query = """
            SELECT 
                s.StockID, s.ProductID, s.SupplierID,
                sup.Name AS SupplierName,
                p.ProductName, s.ExpDate, s.Quantity, s.Damaged, s.Status
            FROM stock s
            JOIN product p ON s.ProductID = p.ProductID
            JOIN supplier sup ON s.SupplierID = sup.SupplierID
            WHERE s.StockID = :stock_id AND s.ProductID = :product_id
        """
        
        try:
            result = db.session.execute(text(check_query), {
                'stock_id': stock_id, 
                'product_id': product_id
            })
            item = result.fetchone()
            
            if not item:
                manual_message = f"No item found with Stock ID: {stock_id} and Product ID: {product_id}"
            else:
                # Check blocking conditions only
                
                # 1. Check if already returned
                if item.Status == 'Returned':
                    manual_message = f"Item with Stock ID: {stock_id} is already returned"
                
                # 2. Check if already exists in returnedstock table
                elif db.session.execute(text("""
                    SELECT 1 FROM returnedstock r 
                    WHERE r.StockID = :stock_id AND r.ProductID = :product_id
                """), {'stock_id': stock_id, 'product_id': product_id}).fetchone():
                    manual_message = f"Item with Stock ID: {stock_id} is already returned"
                
                # 3. Check if out of stock (quantity = 0 and no damage)
                elif item.Quantity == 0 and (item.Damaged is None or item.Damaged == 0):
                    manual_message = f"Item with Stock ID: {stock_id} is out of stock"
                
                # 4. Check if item is expired or damaged (already in upper table)
                elif item.Status == 'Expired' or (item.Damaged is not None and item.Damaged > 0):
                    # Check if it's actually in the returnable items list
                    returnable_check = db.session.execute(text("""
                        SELECT 1 FROM (
                            SELECT s.StockID, s.ProductID
                            FROM stock s
                            WHERE ((s.Status = 'Expired' AND s.Quantity != 0) OR s.Damaged > 0)
                            AND s.Status != 'Returned'
                            AND NOT EXISTS (
                                SELECT 1 FROM returnedstock r 
                                WHERE r.StockID = s.StockID AND r.ProductID = s.ProductID
                            )
                        ) AS returnable
                        WHERE returnable.StockID = :stock_id AND returnable.ProductID = :product_id
                    """), {'stock_id': stock_id, 'product_id': product_id}).fetchone()
                    
                    if returnable_check:
                        if item.Status == 'Expired':
                            manual_message = f"Item with Stock ID: {stock_id} is expired and already listed in the returnable items table above"
                        else:
                            manual_message = f"Item with Stock ID: {stock_id} is damaged and already listed in the returnable items table above"
                    else:
                        # Show item details even if expired/damaged but not in returnable list
                        manual_item = item
                
                # 5. Item is available for manual return - show details
                else:
                    manual_item = item
                
        except Exception as e:
            manual_message = f"Error fetching item: {str(e)}"
    else:
        manual_message = "Please provide both Stock ID and Product ID"

    # Render template with BOTH Section A data (preserved) AND Section B data (new lookup)
    return render_template("supplier_returns.html",
                         returns=data['returns'],              # Section A - preserved
                         reason_filter=current_reason_filter,   # Section A - preserved  
                         current_page=current_page,             # Section A - preserved
                         total_pages=data['total_pages'],       # Section A - preserved
                         manual_item=manual_item,               # Section B - item details to show
                         manual_message=manual_message)         # Section B - warning/error messages