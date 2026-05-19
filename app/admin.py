from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flasgger import swag_from

from app import db
from app.middleware import admin_required
from app.models import User, MentorProfile, Review


admin = Blueprint("admin", __name__)


@admin.get("/api/admin/users")
@jwt_required()
@admin_required
@swag_from({
    "tags": ["Admin"],
    "summary": "Admin can view all users"
})
def get_all_users():
    users = User.query.all()

    return jsonify([
        user.to_dict()
        for user in users
    ]), 200


@admin.get("/api/admin/mentor-profiles")
@jwt_required()
@admin_required
@swag_from({
    "tags": ["Admin"],
    "summary": "Admin can view all mentor profiles"
})
def admin_get_mentor_profiles():
    profiles = MentorProfile.query.all()

    return jsonify([
        profile.to_dict()
        for profile in profiles
    ]), 200


@admin.get("/api/admin/reviews")
@jwt_required()
@admin_required
@swag_from({
    "tags": ["Admin"],
    "summary": "Admin can view all reviews"
})
def admin_get_reviews():
    reviews = Review.query.all()

    return jsonify([
        review.to_dict()
        for review in reviews
    ]), 200


@admin.delete("/api/admin/reviews/<int:id>")
@jwt_required()
@admin_required
@swag_from({
    "tags": ["Admin"],
    "summary": "Admin can delete a review"
})
def admin_delete_review(id):
    review = Review.query.get_or_404(id)

    db.session.delete(review)
    db.session.commit()

    return jsonify({
        "message": "Review deleted successfully"
    }), 200


@admin.delete("/api/admin/mentor-profiles/<int:id>")
@jwt_required()
@admin_required
@swag_from({
    "tags": ["Admin"],
    "summary": "Admin can delete a mentor profile"
})
def admin_delete_mentor_profile(id):
    profile = MentorProfile.query.get_or_404(id)

    db.session.delete(profile)
    db.session.commit()

    return jsonify({
        "message": "Mentor profile deleted successfully"
    }), 200