import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/blog_app")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "static/uploads")
