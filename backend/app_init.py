from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, sys
from flask_login import LoginManager
from sqlalchemy import text

# Enable import of local files
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'  # Redirect to login page if not logged in

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.secret_key = 'Waseek-123456'

    db.init_app(app)
    login_manager.init_app(app)

    # ✅ Register Blueprints
    from controllers.db_test_controller import test_bp
    from controllers.brand_controller import brand_bp
    from controllers.ui_controller import ui_bp
    from controllers.product_controller import product_bp
    from controllers.auth_controller import auth_bp  # <- ADD THIS
    from controllers.order_controller import order_bp
    from controllers.stock_controller import stock_bp
    from controllers.returnproduct_controller import returnproduct_bp
    from controllers.supplier_controller import supplier_bp
    from controllers.employee_controller import employee_bp
    from controllers.dashboard import dashboard_bp 


    app.register_blueprint(test_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(auth_bp)  # <- ADD THIS
    app.register_blueprint(order_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(returnproduct_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(dashboard_bp)
    return app

# ✅ Import your custom EmployeeUser class
from models.models import EmployeeUser

@login_manager.user_loader
def load_user(user_id):
    result = db.session.execute(
        text("SELECT * FROM Employee WHERE EmployeeID = :id"),
        {'id': user_id}
    ).fetchone()
    return EmployeeUser(result) if result else None
