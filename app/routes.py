from flask import Blueprint, jsonify

main = Blueprint("main", __name__)

@main.get("/")
def index():
    return jsonify({"message": "Welcome to HustleHub API"})

@main.get("/api/health")
def health():
    return jsonify({"status": "ok", "message": "HustleHub API is running"})