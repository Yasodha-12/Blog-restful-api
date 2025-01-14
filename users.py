from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_login import UserMixin
from utils.auth import generate_token, verify_token, login_required, admin_required
from datetime import datetime


class AccountModel(UserMixin):
    def __init__(self, database):
        self.account_collection = database.users

    def register_routes(self, application):
        @application.route("/register", methods=["POST"])
        def register_account():
            payload = request.json
            if not payload.get("username") or not payload.get("password"):
                return jsonify({"error": "Username and password are required"}), 400
            if self.account_collection.find_one({"username": payload["username"]}):
                return jsonify({"error": "Username already exists"}), 400

            hashed_password = generate_password_hash(payload["password"])
            account = {
                "username": payload["username"],
                "email": payload.get("email"),
                "password": hashed_password,
                "role": "viewer",
                "bio": "",
                "profile_pic": "",
                "followers": [],
                "following": [],
                "created_at": datetime.utcnow(),
            }
            self.account_collection.insert_one(account)
            return jsonify({"message": "Account registered successfully"}), 201

        @application.route("/login", methods=["POST"])
        def login_account():
            payload = request.json
            account = self.account_collection.find_one({"username": payload["username"]})
            if not account or not check_password_hash(account["password"], payload["password"]):
                return jsonify({"error": "Invalid credentials"}), 401
            token = generate_token(str(account["_id"]), account["role"])
            return jsonify({"token": token}), 200

        @application.route("/profile", methods=["GET", "PUT"])
        @login_required
        def account_profile(account_id):
            account = self.account_collection.find_one({"_id": ObjectId(account_id)})
            if not account:
                return jsonify({"error": "Account not found"}), 404

            if request.method == "GET":
                account["_id"] = str(account["_id"])
                del account["password"]
                return jsonify(account), 200

            payload = request.json
            self.account_collection.update_one({"_id": ObjectId(account_id)}, {"$set": payload})
            return jsonify({"message": "Profile updated successfully"}), 200

        @application.route("/users/<string:account_id>/follow", methods=["POST"])
        @login_required
        def follow_account(account_id, follow_account_id):
            account = self.account_collection.find_one({"_id": ObjectId(account_id)})
            follow_account = self.account_collection.find_one({"_id": ObjectId(follow_account_id)})

            if not account or not follow_account:
                return jsonify({"error": "Account not found"}), 404

            if follow_account_id in account["following"]:
                return jsonify({"message": "Already following"}), 400

            self.account_collection.update_one(
                {"_id": ObjectId(account_id)}, {"$addToSet": {"following": follow_account_id}}
            )
            self.account_collection.update_one(
                {"_id": ObjectId(follow_account_id)}, {"$addToSet": {"followers": account_id}}
            )

            return jsonify({"message": "Followed successfully"}), 200

        @application.route("/users/<string:account_id>/unfollow", methods=["POST"])
        @login_required
        def unfollow_account(account_id, unfollow_account_id):
            account = self.account_collection.find_one({"_id": ObjectId(account_id)})
            unfollow_account = self.account_collection.find_one({"_id": ObjectId(unfollow_account_id)})

            if not account or not unfollow_account:
                return jsonify({"error": "Account not found"}), 404

            if unfollow_account_id not in account["following"]:
                return jsonify({"message": "Not following this account"}), 400

            self.account_collection.update_one(
                {"_id": ObjectId(account_id)}, {"$pull": {"following": unfollow_account_id}}
            )
            self.account_collection.update_one(
                {"_id": ObjectId(unfollow_account_id)}, {"$pull": {"followers": account_id}}
            )

            return jsonify({"message": "Unfollowed successfully"}), 200
