from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app import db
from app.models import User, MentorProfile, Review


mentor_profiles = Blueprint("mentor_profiles", __name__)


@mentor_profiles.post("/api/mentor-profile")
@jwt_required()
@swag_from({
    "tags": ["Mentors"],
    "summary": "Create or update mentor profile",
    "responses": {
        200: {"description": "Mentor profile saved"},
        401: {"description": "Unauthorized"}
    }
})
def create_or_update_mentor_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    profile = MentorProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        profile = MentorProfile(user_id=user.id)
        db.session.add(profile)

    user.role = "mentor"

    profile.bio = data.get("bio", profile.bio)
    profile.niche = data.get("niche", profile.niche)
    profile.skills = data.get("skills", profile.skills)
    profile.availability = data.get("availability", profile.availability)
    profile.price = data.get("price", profile.price)
    profile.github_url = data.get("github_url", profile.github_url)
    profile.linkedin_url = data.get("linkedin_url", profile.linkedin_url)
    profile.portfolio_url = data.get("portfolio_url", profile.portfolio_url)
    profile.contact_email = data.get("contact_email", profile.contact_email)

    db.session.commit()

    return jsonify({
        "message": "Mentor profile saved!",
        "mentor_profile": profile.to_dict(),
        "user": user.to_dict()
    }), 200


@mentor_profiles.get("/api/mentor-profile/me")
@jwt_required()
@swag_from({
    "tags": ["Mentors"],
    "summary": "Get current user's mentor profile"
})
def get_my_mentor_profile():
    user_id = int(get_jwt_identity())

    profile = MentorProfile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        return jsonify({
            "error": "Mentor profile not found"
        }), 404

    return jsonify(profile.to_dict()), 200


@mentor_profiles.get("/api/mentor-profiles")
@swag_from({
    "tags": ["Mentors"],
    "summary": "Get all mentor profiles"
})
def get_all_mentor_profiles():
    profiles = MentorProfile.query.all()

    return jsonify([
        profile.to_dict()
        for profile in profiles
    ]), 200


@mentor_profiles.get("/api/mentor-profiles/<int:id>")
@swag_from({
    "tags": ["Mentors"],
    "summary": "Get one mentor profile"
})
def get_one_mentor_profile(id):
    profile = MentorProfile.query.get_or_404(id)

    return jsonify(profile.to_dict()), 200


@mentor_profiles.post("/api/mentor-profiles/<int:id>/reviews")
@jwt_required()
@swag_from({
    "tags": ["Reviews"],
    "summary": "Add review to mentor profile",
    "responses": {
        201: {"description": "Review added"},
        400: {"description": "Validation error"},
        403: {"description": "Cannot review yourself"}
    }
})
def add_review(id):
    user_id = int(get_jwt_identity())

    profile = MentorProfile.query.get_or_404(id)

    if profile.user_id == user_id:
        return jsonify({
            "error": "You cannot review your own mentor profile"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    rating = data.get("rating")

    if not rating:
        return jsonify({
            "error": "Rating is required"
        }), 400

    rating = int(rating)

    if rating < 1 or rating > 5:
        return jsonify({
            "error": "Rating must be between 1 and 5"
        }), 400

    review = Review(
        mentor_profile_id=profile.id,
        user_id=user_id,
        rating=rating,
        comment=data.get("comment")
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        "message": "Review added!",
        "review": review.to_dict()
    }), 201


@mentor_profiles.get("/api/mentor-profiles/<int:id>/reviews")
@swag_from({
    "tags": ["Reviews"],
    "summary": "Get mentor profile reviews"
})
def get_reviews(id):
    profile = MentorProfile.query.get_or_404(id)

    return jsonify([
        review.to_dict()
        for review in profile.reviews
    ]), 200