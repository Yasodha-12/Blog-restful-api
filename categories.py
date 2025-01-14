from flask import request, jsonify
from bson.objectid import ObjectId
from utils.auth import admin_required


class CategoryModel:
    def __init__(self, db):
        self.collection = db.categories

    def register_routes(self, app):
        @app.route("/categories", methods=["POST", "GET"])
        @admin_required
        def manage_categories(user_id):
            if request.method == "POST":
                data = request.json
                if not data.get("name"):
                    return jsonify({"error": "Category name is required"}), 400

                category = {"name": data["name"]}
                self.collection.insert_one(category)
                return jsonify({"message": "Category created"}), 201

            categories = list(self.collection.find())
            for category in categories:
                category["_id"] = str(category["_id"])
            return jsonify(categories), 200
