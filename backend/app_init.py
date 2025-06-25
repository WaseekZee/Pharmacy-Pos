from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, sys

# Enable import of local files
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

db = SQLAlchemy()  # Global DB object (correct)

def create_app():
    app = Flask(__name__)  # This is the actual app instance used
    app.config.from_pyfile('config.py')

    # ✅ Set secret key here, where the app is being configured
    app.secret_key = 'Waseek-123456'

    db.init_app(app)

    # Register blueprints
    from controllers.db_test_controller import test_bp
    from controllers.brand_controller import brand_bp
    from controllers.ui_controller import ui_bp

    app.register_blueprint(test_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(ui_bp)

    return app


