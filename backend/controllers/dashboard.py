from flask import Blueprint, render_template, request, flash
from app_init import db
from sqlalchemy import text

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def dashboard():
    # Top-selling products
    top_selling_products = db.session.execute(text("""
        SELECT p.ProductName, SUM(ps.Quantity) AS total_sold, SUM(ps.Quantity * s.SellingPrice) AS total_revenue
        FROM pack ps
        JOIN product p ON ps.ProductID = p.ProductID
        JOIN stock s ON ps.ProductID = s.ProductID
        GROUP BY p.ProductName
        ORDER BY total_sold DESC
        LIMIT 5
    """)).fetchall()

    # Least-selling products
    least_selling_products = db.session.execute(text("""
        SELECT p.ProductName, SUM(ps.Quantity) AS total_sold
        FROM pack ps
        JOIN product p ON ps.ProductID = p.ProductID
        GROUP BY p.ProductName
        ORDER BY total_sold ASC
        LIMIT 5
    """)).fetchall()

    # Total sales for the month
    total_sales = db.session.execute(text("""
        SELECT SUM(ps.Quantity * s.SellingPrice) AS total_sales
        FROM pack ps
        JOIN stock s ON ps.StockID = s.StockID
        WHERE ps.Date >= '2025-07-01' AND ps.Date <= '2025-07-31'
    """)).scalar()

    # Sales Trend (for this example, we are getting monthly sales data)
    sales_trend_data = db.session.execute(text("""
        SELECT MONTH(ps.Date) AS month, SUM(ps.Quantity * s.SellingPrice) AS total_sales
        FROM pack ps
        JOIN stock s ON ps.StockID = s.StockID
        GROUP BY MONTH(ps.Date)
    """)).fetchall()

    # Prepare data for the sales trend graph
    sales_trend_labels = [str(row[0]) for row in sales_trend_data]  # Month numbers
    sales_trend_values = [row[1] for row in sales_trend_data]  # Sales amounts

    return render_template('dashboard.html', 
                           top_selling_products=top_selling_products,
                           least_selling_products=least_selling_products,
                           total_sales=total_sales,
                           sales_trend_labels=sales_trend_labels,
                           sales_trend_values=sales_trend_values)
