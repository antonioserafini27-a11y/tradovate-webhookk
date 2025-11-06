from flask import Blueprint, jsonify
from models import get_trades


api_bp = Blueprint("api", __name__)


@api_bp.route("/trades", methods=["GET"])
def list_trades():
trades = get_trades()
return jsonify([
{
"id": row[0],
"action": row[1],
"symbol": row[2],
"price": row[3],
"quantity": row[4],
"timestamp": row[5],
}
for row in trades
])
