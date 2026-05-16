from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(500), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorites = db.relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        from app import bcrypt
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        from app import bcrypt
        return bcrypt.check_password_hash(self.password, raw_password)

    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "email": self.email,
            "profile_image": self.profile_image,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    item_id = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)

    title = db.Column(db.String(255), nullable=False)

    cover = db.Column(db.String(500), nullable=True)
    author = db.Column(db.String(255), nullable=True)

    login = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="favorites")

    def to_dict(self):
        if self.item_type == "mentor":
            return {
                "id": self.id,
                "item_id": self.item_id,
                "type": "mentor",
                "name": self.title,
                "login": self.login or "",
                "avatar": self.avatar or "https://placehold.co/120x120?text=No+Image",
                "bio": self.bio or "This mentor has no bio yet.",
                "created_at": self.created_at.isoformat(),
            }

        return {
            "id": self.id,
            "item_id": self.item_id,
            "type": "book",
            "title": self.title,
            "author": self.author or "Unknown Author",
            "cover": self.cover or "https://placehold.co/250x340?text=No+Image",
            "created_at": self.created_at.isoformat(),
        }