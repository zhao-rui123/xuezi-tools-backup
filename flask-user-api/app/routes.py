from flask import Blueprint, request, jsonify
from app import db
from app.models import User

api_bp = Blueprint("api", __name__)


@api_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@api_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("email"):
        return jsonify({"error": "username and email are required"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "username already exists"}), 409
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "email already exists"}), 409

    user = User(username=data["username"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@api_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user.to_dict())


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request"}), 400

    if "username" in data:
        existing = User.query.filter_by(username=data["username"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "username already exists"}), 409
        user.username = data["username"]

    if "email" in data:
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "email already exists"}), 409
        user.email = data["email"]

    db.session.commit()
    return jsonify(user.to_dict())


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "deleted"}), 200
