from flask import Blueprint, render_template, request, redirect, url_for, flash
from app_init import db
from sqlalchemy import text

product_bp = Blueprint('product_bp', __name__, url_prefix='/products')

@product_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['productName']
        description = request.form['description']
        brand_id = request.form['brand']
        category = request.form['category']  # ✅ Fixed this line

        try:
            db.session.execute(
                text("""
                    INSERT INTO Product (ProductName, Description, BrandID, category)
                    VALUES (:name, :desc, :brand_id, :category)
                """),
                {
                    "name": name,
                    "desc": description,
                    "brand_id": brand_id,
                    "category": category  # ✅ Make sure to pass the value
                }
            )
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('product_bp.add_product'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
            return redirect(url_for('product_bp.add_product'))

    # GET request – fetch brands and existing products
    brands = db.session.execute(text("SELECT BrandID, Name FROM Brand")).fetchall()
    products = db.session.execute(text("""
        SELECT p.ProductID, p.ProductName AS name, p.Description AS description, b.Name AS brand_name, p.category
        FROM Product p
        JOIN Brand b ON p.BrandID = b.BrandID
    """)).fetchall()

    return render_template("product.html", brands=brands, products=products)


@product_bp.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        db.session.execute(text("DELETE FROM Product WHERE ProductID = :id"), {'id': product_id})
        db.session.commit()
        flash("Product deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting product: {e}", "danger")
    return redirect(url_for('product_bp.view_products', _anchor='view-tab'))
