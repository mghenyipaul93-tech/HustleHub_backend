from app import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(120), nullable=False)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password      = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(500), nullable=True)
    role          = db.Column(db.String(20), nullable=False, default="user")
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password, raw_password)

    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        return {
            "id":            self.id,
            "full_name":     self.full_name,
            "username":      self.username,
            "email":         self.email,
            "profile_image": self.profile_image,
            "role":          self.role,
            "created_at":    self.created_at.isoformat(),
        }