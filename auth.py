from flask import request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta

# Define SECRET_KEY directly in the script
SECRET_KEY = "fff241e3eb88c5e76341a04264d65f2401be729cd07ceeb0b6102834d1bcaa64"

def generate_token(user_id, role):
    """
    Generates a JWT token for a user.
    """
    expiration = datetime.utcnow() + timedelta(days=1)
    payload = {"user_id": user_id, "role": role, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    """
    Verifies the validity of a JWT token.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("Decoded Token:", decoded)  # Debug line
        return decoded
    except jwt.ExpiredSignatureError:
        print("Token expired")  # Debug line
        return None
    except jwt.InvalidTokenError as e:
        print("Invalid Token:", str(e))  # Debug line
        return None

def login_required(func):
    """
    Decorator to protect routes for authenticated users.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Token is required"}), 401
        
        # Support "Bearer <token>" format in the Authorization header
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        else:
            token = auth_header  # Assume raw token

        user = verify_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401
        return func(user["user_id"], *args, **kwargs)
    return wrapper

def admin_required(func):
    """
    Decorator to protect routes for admin users.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Token is required"}), 401
        
        # Support "Bearer <token>" format in the Authorization header
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        else:
            token = auth_header  # Assume raw token

        user = verify_token(token)
        if not user or user["role"] != "admin":
            return jsonify({"error": "Admin privileges required"}), 403
        return func(user["user_id"], *args, **kwargs)
    return wrapper
