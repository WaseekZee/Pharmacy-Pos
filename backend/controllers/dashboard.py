from flask import Blueprint, render_template, request, flash
from app_init import db
from sqlalchemy import text

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def dashboard():
    # Top-selling products
    top_selling_products_raw = db.session.execute(text("""
        SELECT p.ProductName, SUM(ps.Quantity) AS total_sold, SUM(ps.Quantity * s.SellingPrice) AS total_revenue
        FROM pack ps
        JOIN product p ON ps.ProductID = p.ProductID
        JOIN stock s ON ps.ProductID = s.ProductID
        GROUP BY p.ProductName
        ORDER BY total_sold DESC
        LIMIT 5
    """)).fetchall()
    
    # Convert to dictionaries
    top_selling_products = [
        {
            'ProductName': row.ProductName,
            'total_sold': int(row.total_sold) if row.total_sold else 0,
            'total_revenue': float(row.total_revenue) if row.total_revenue else 0.0
        }
        for row in top_selling_products_raw
    ]

    # Least-selling products
    least_selling_products_raw = db.session.execute(text("""
        SELECT p.ProductName, SUM(ps.Quantity) AS total_sold
        FROM pack ps
        JOIN product p ON ps.ProductID = p.ProductID
        GROUP BY p.ProductName
        ORDER BY total_sold ASC
        LIMIT 5
    """)).fetchall()
    
    # Convert to dictionaries
    least_selling_products = [
        {
            'ProductName': row.ProductName,
            'total_sold': int(row.total_sold) if row.total_sold else 0
        }
        for row in least_selling_products_raw
    ]

    # Total sales for the month
    total_sales_raw = db.session.execute(text("""
        SELECT SUM(ps.Quantity * s.SellingPrice) AS total_sales
        FROM pack ps
        JOIN stock s ON ps.StockID = s.StockID
        WHERE ps.Date >= '2025-07-01' AND ps.Date <= '2025-07-31'
    """)).scalar()
    
    total_sales = float(total_sales_raw) if total_sales_raw else 0.0

    # Sales Trend (for this example, we are getting monthly sales data)
    sales_trend_data_raw = db.session.execute(text("""
        SELECT MONTH(ps.Date) AS month, SUM(ps.Quantity * s.SellingPrice) AS total_sales
        FROM pack ps
        JOIN stock s ON ps.StockID = s.StockID
        GROUP BY MONTH(ps.Date)
        ORDER BY MONTH(ps.Date)
    """)).fetchall()

    # Convert month numbers to month names
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
    # Prepare data for the sales trend graph
    sales_trend_labels = [month_names.get(row.month, str(row.month)) for row in sales_trend_data_raw]
    sales_trend_values = [float(row.total_sales) if row.total_sales else 0.0 for row in sales_trend_data_raw]

    return render_template('dashboard.html',
                          top_selling_products=top_selling_products,
                          least_selling_products=least_selling_products,
                          total_sales=total_sales,
                          sales_trend_labels=sales_trend_labels,
                          sales_trend_values=sales_trend_values, active_page="dashboard" )
