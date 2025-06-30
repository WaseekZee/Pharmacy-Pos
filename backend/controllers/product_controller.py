from flask import Blueprint, render_template, request, redirect, url_for, flash
from app_init import db
from sqlalchemy import text

product_bp = Blueprint('product_bp', __name__, url_prefix='/products')


# ------------------ Add Product ------------------
@product_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['productName']
        description = request.form['description']
        brand_id = request.form['brand']
        category = request.form['category']

        try:
            db.session.execute(
                text("""
                    INSERT INTO Product (ProductName, Description, BrandID, Category)
                    VALUES (:name, :desc, :brand_id, :category)
                """),
                {
                    "name": name,
                    "desc": description,
                    "brand_id": brand_id,
                    "category": category
                }
            )
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('product_bp.add_product'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
            return redirect(url_for('product_bp.add_product'))

    brands = db.session.execute(text("SELECT BrandID, Name FROM Brand")).fetchall()
    return render_template("add_product.html", brands=brands)


# ------------------ View Products ------------------
@product_bp.route('/view', methods=['GET'])
def view_products():
    products = db.session.execute(text("""
        SELECT p.ProductID, p.ProductName AS name, p.Description AS description,
               p.Category AS category, p.BrandID, b.Name AS brand_name
        FROM Product p
        JOIN Brand b ON p.BrandID = b.BrandID
    """)).fetchall()

    brands = db.session.execute(text("SELECT BrandID, Name FROM Brand")).fetchall()

    return render_template("view_products.html", products=products, brands=brands)


# ------------------ Edit Product ------------------
@product_bp.route('/edit/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    new_name = request.form['editProductName']
    new_description = request.form['editDescription']
    new_category = request.form['editCategory']
    new_brand_id = request.form['editBrand']

    try:
        db.session.execute(
            text("""
                UPDATE Product
                SET ProductName = :name,
                    Description = :description,
                    Category = :category,
                    BrandID = :brand_id
                WHERE ProductID = :id
            """),
            {
                'name': new_name,
                'description': new_description,
                'category': new_category,
                'brand_id': new_brand_id,
                'id': product_id
            }
        )
        db.session.commit()
        flash("Product updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating product: {e}", "danger")

    return redirect(url_for('product_bp.view_products'))


# ------------------ Delete Product ------------------
@product_bp.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        db.session.execute(
            text("DELETE FROM Product WHERE ProductID = :id"),
            {'id': product_id}
        )
        db.session.commit()
        flash("Product deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting product: {e}", "danger")

    return redirect(url_for('product_bp.view_products'))
