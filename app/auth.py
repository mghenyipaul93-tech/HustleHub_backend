from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from flasgger import swag_from

from app import db
from app.models import User
from app.middleware import admin_required
from app.send_email import send_welcome_email

import cloudinary.uploader
from app.cloudinary_config import *


auth = Blueprint("auth", __name__)


@auth.post("/api/auth/register")
@swag_from({
    "tags": ["Authentication"],
    "summary": "Register a new user",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "full_name": {"type": "string"},
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        201: {"description": "Account created"},
        400: {"description": "Validation error"},
        409: {"description": "User already exists"}
    }
})
def register():
    data = request.get_json()

    if not data.get("full_name"):
        return jsonify({"error": "Full name is required"}), 400

    if not data.get("username"):
        return jsonify({"error": "Username is required"}), 400

    if not data.get("email"):
        return jsonify({"error": "Email is required"}), 400

    if not data.get("password"):
        return jsonify({"error": "Password is required"}), 400

    if len(data["password"]) < 6:
        return jsonify({
            "error": "Password must be at least 6 characters"
        }), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({
            "error": "Email already registered"
        }), 409

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({
            "error": "Username already taken"
        }), 409

    user = User(
        full_name=data["full_name"],
        username=data["username"],
        email=data["email"],
    )

    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    send_welcome_email(user.email, user.username)

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Account created!",
        "token": token,
        "user": user.to_dict()
    }), 201


@auth.post("/api/auth/login")
@swag_from({
    "tags": ["Authentication"],
    "summary": "Login user",
    "responses": {
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"}
    }
})
def login():
    data = request.get_json()

    if not data.get("email"):
        return jsonify({"error": "Email is required"}), 400

    if not data.get("password"):
        return jsonify({"error": "Password is required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful!",
        "token": token,
        "user": user.to_dict()
    }), 200


@auth.get("/api/auth/me")
@jwt_required()
@swag_from({
    "tags": ["Authentication"],
    "summary": "Get current user"
})
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    return jsonify(user.to_dict()), 200


@auth.get("/api/profile")
@jwt_required()
@swag_from({
    "tags": ["Profile"],
    "summary": "Get user profile"
})
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    return jsonify(user.to_dict()), 200


@auth.patch("/api/profile")
@jwt_required()
@swag_from({
    "tags": ["Profile"],
    "summary": "Update user profile"
})
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if data.get("full_name"):
        user.full_name = data.get("full_name")

    if data.get("username"):
        existing_username = User.query.filter_by(
            username=data.get("username")
        ).first()

        if existing_username and existing_username.id != user.id:
            return jsonify({
                "error": "Username already taken"
            }), 409

        user.username = data.get("username")

    if data.get("email"):
        existing_email = User.query.filter_by(
            email=data.get("email")
        ).first()

        if existing_email and existing_email.id != user.id:
            return jsonify({
                "error": "Email already registered"
            }), 409

        user.email = data.get("email")

    db.session.commit()

    return jsonify({
        "message": "Profile updated!",
        "user": user.to_dict()
    }), 200


@auth.post("/api/auth/upload-profile-image")
@jwt_required()
@swag_from({
    "tags": ["Profile"],
    "summary": "Upload profile image"
})
def upload_profile_image():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if "image" not in request.files:
        return jsonify({
            "error": "Image file is required"
        }), 400

    image = request.files["image"]

    upload_result = cloudinary.uploader.upload(image)

    image_url = upload_result["secure_url"]

    user.profile_image = image_url

    db.session.commit()

    return jsonify({
        "message": "Profile image uploaded!",
        "profile_image": image_url,
        "user": user.to_dict()
    }), 200


@auth.get("/api/auth/admin")
@jwt_required()
@admin_required
@swag_from({
    "tags": ["Admin"],
    "summary": "Admin-only route"
})
def admin_only():
    return jsonify({
        "message": "Welcome Admin!"
    }), 200


@auth.patch("/api/auth/become-mentor")
@jwt_required()
@swag_from({
    "tags": ["Mentors"],
    "summary": "Become a mentor"
})
def become_mentor():
    user_id = int(get_jwt_identity())

    user = User.query.get_or_404(user_id)

    user.role = "mentor"

    db.session.commit()

    return jsonify({
        "message": "You are now a mentor!",
        "user": user.to_dict()
    }), 200