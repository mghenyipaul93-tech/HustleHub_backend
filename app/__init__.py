from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    @app.get("/")
    def index():
        return {"message": "Welcome to HustleHub API 🚀"}

    @app.get("/api/health")
    def health():
        return {"status": "ok", "message": "HustleHub API is running 🚀"}

    return app