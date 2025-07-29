from flask import Blueprint, render_template, request, redirect, url_for, flash
from app_init import db
from sqlalchemy import text
from flask_login import login_required


product_bp = Blueprint('product_bp', __name__, url_prefix='/products')


# ------------------ Add Product ------------------
@product_bp.route('/add', methods=['GET', 'POST'])
@login_required
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
    return render_template("add_product.html", brands=brands , active_page="product")


# ------------------ View Products ------------------
@product_bp.route('/view', methods=['GET'])
@login_required
def view_products():
    # Get current page from query string
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Items per page
    offset = (page - 1) * per_page

    # Fetch paginated products
    products = db.session.execute(text("""
        SELECT p.ProductID, p.ProductName AS name, p.Description AS description,
               p.Category AS category, p.BrandID, b.Name AS brand_name
        FROM Product p
        JOIN Brand b ON p.BrandID = b.BrandID
        LIMIT :limit OFFSET :offset
    """), {"limit": per_page, "offset": offset}).fetchall()

    # Fetch total product count
    total_count = db.session.execute(text("SELECT COUNT(*) FROM Product")).scalar()
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division

    # Fetch all brands
    brands = db.session.execute(text("SELECT BrandID, Name FROM Brand")).fetchall()

    return render_template("view_products.html",
                           products=products,
                           brands=brands,
                           page=page,
                           total_pages=total_pages,
                           active_page="product")



# ------------------ Edit Product ------------------
@product_bp.route('/edit/<int:product_id>', methods=['POST'])
@login_required
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
from sqlalchemy.exc import IntegrityError
from flask import flash, redirect, url_for

@product_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    try:
        db.session.execute(
            text("DELETE FROM Product WHERE ProductID = :id"),
            {'id': product_id}
        )
        db.session.commit()
        flash("✅ Product deleted successfully!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("❌ Cannot delete product: It is associated with existing orders.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ An unexpected error occurred: {str(e)}", "danger")

    return redirect(url_for('product_bp.view_products'))

