from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
from app.middleware import admin_required

auth = Blueprint("auth", __name__)

@auth.post("/api/auth/register")
def register():
    data = request.get_json()

    # validation
    if not data.get("full_name"):
        return jsonify({"error": "Full name is required"}), 400
    if not data.get("username"):
        return jsonify({"error": "Username is required"}), 400
    if not data.get("email"):
        return jsonify({"error": "Email is required"}), 400
    if not data.get("password"):
        return jsonify({"error": "Password is required"}), 400
    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409

    user = User(
        full_name = data["full_name"],
        username  = data["username"],
        email     = data["email"],
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Account created!",
        "token":   token,
        "user":    user.to_dict()
    }), 201


@auth.post("/api/auth/login")
def login():
    data = request.get_json()

    if not data.get("email"):
        return jsonify({"error": "Email is required"}), 400
    if not data.get("password"):
        return jsonify({"error": "Password is required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful!",
        "token":   token,
        "user":    user.to_dict()
    }), 200


@auth.get("/api/auth/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@auth.get("/api/auth/admin")
@jwt_required()
@admin_required
def admin_only():
    return jsonify({"message": "Welcome Admin!"}), 200