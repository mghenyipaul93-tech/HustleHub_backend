from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Favorite

favorites = Blueprint("favorites", __name__)


# GET all favorites for current user
@favorites.get("/api/favorites")
@jwt_required()
def get_favorites():
    user_id = int(get_jwt_identity())

    all_favs = Favorite.query.filter_by(user_id=user_id).all()

    return jsonify([favorite.to_dict() for favorite in all_favs]), 200


# POST add a favorite
@favorites.post("/api/favorites")
@jwt_required()
def add_favorite():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    if not data.get("item_id"):
        return jsonify({"error": "item_id is required"}), 400

    if not data.get("item_type"):
        return jsonify({"error": "item_type is required"}), 400

    if not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    existing = Favorite.query.filter_by(
        user_id=user_id,
        item_id=str(data.get("item_id")),
        item_type=data.get("item_type")
    ).first()

    if existing:
        return jsonify({"error": "Already in favorites"}), 409

    favorite = Favorite(
        user_id=user_id,
        item_id=str(data.get("item_id")),
        item_type=data.get("item_type"),
        title=data.get("title"),

        cover=data.get("cover"),
        author=data.get("author"),

        login=data.get("login"),
        avatar=data.get("avatar"),
        bio=data.get("bio"),
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({
        "message": "Added to favorites!",
        "favorite": favorite.to_dict()
    }), 201


# DELETE remove a favorite
@favorites.delete("/api/favorites/<int:id>")
@jwt_required()
def delete_favorite(id):
    user_id = int(get_jwt_identity())

    favorite = Favorite.query.get_or_404(id)

    if favorite.user_id != user_id:
        return jsonify({"error": "Permission denied"}), 403

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Removed from favorites!"}), 200