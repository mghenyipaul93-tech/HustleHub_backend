from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Favorite, User

favorites = Blueprint("favorites", __name__)


@favorites.get("/api/favorites")
@jwt_required()
def get_favorites():
    user_id = int(get_jwt_identity())

    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    if page and per_page:
        paginated_favs = Favorite.query.filter_by(user_id=user_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            "favorites": [favorite.to_dict() for favorite in paginated_favs.items],
            "page": paginated_favs.page,
            "per_page": paginated_favs.per_page,
            "total": paginated_favs.total,
            "pages": paginated_favs.pages
        }), 200

    all_favs = Favorite.query.filter_by(user_id=user_id).all()

    return jsonify([favorite.to_dict() for favorite in all_favs]), 200


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

    if data.get("item_type") not in ["mentor", "book"]:
        return jsonify({"error": "item_type must be mentor or book"}), 400

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


@favorites.delete("/api/favorites/<int:id>")
@jwt_required()
def delete_favorite(id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    favorite = Favorite.query.get_or_404(id)

    if favorite.user_id != user.id and not user.is_admin():
        return jsonify({"error": "Permission denied"}), 403

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Removed from favorites!"}), 200


@favorites.get("/api/admin/favorites")
@jwt_required()
def get_all_favorites():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if not user.is_admin():
        return jsonify({"error": "Admin access required"}), 403

    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    if page and per_page:
        paginated_favs = Favorite.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            "favorites": [favorite.to_dict() for favorite in paginated_favs.items],
            "page": paginated_favs.page,
            "per_page": paginated_favs.per_page,
            "total": paginated_favs.total,
            "pages": paginated_favs.pages
        }), 200

    all_favs = Favorite.query.all()

    return jsonify([favorite.to_dict() for favorite in all_favs]), 200