from flask import Blueprint, jsonify
from app_init import db
from sqlalchemy import text

test_bp = Blueprint('test_bp', __name__, url_prefix='/api/test')

@test_bp.route('/', methods=['GET'])
def get_stock():
    try:
        result = db.session.execute(text("SELECT * FROM Stock"))
        stock_list = [dict(row._mapping) for row in result]
        return jsonify(stock_list)
    except Exception as e:
        return jsonify({"error": str(e)})
