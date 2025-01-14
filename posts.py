from flask import request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from utils.auth import login_required, admin_required
import os


class PostModel:
    def __init__(self, db):
        self.collection = db.posts

    def register_routes(self, app):
        @app.route("/posts", methods=["POST"])
        @login_required
        def create_post(user_id):
            data = request.json
            if not data.get("title") or not data.get("content"):
                return jsonify({"error": "Title and content are required"}), 400

            post = {
                "title": data["title"],
                "content": data["content"],
                "author": ObjectId(user_id),
                "views": 0,
                "likes": [],
                "categories": data.get("categories", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            self.collection.insert_one(post)
            return jsonify({"message": "Post created successfully"}), 201

        @app.route("/posts/<string:post_id>", methods=["GET"])
        def get_post(post_id):
            post = self.collection.find_one({"_id": ObjectId(post_id)})
            if not post:
                return jsonify({"error": "Post not found"}), 404

            self.collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"views": 1}})
            post["_id"] = str(post["_id"])
            post["author"] = str(post["author"])
            return jsonify(post), 200

        @app.route("/posts/<string:post_id>", methods=["PUT", "DELETE"])
        @login_required
        def manage_post(user_id, post_id):
            post = self.collection.find_one({"_id": ObjectId(post_id)})
            if not post:
                return jsonify({"error": "Post not found"}), 404

            if str(post["author"]) != user_id:
                return jsonify({"error": "Unauthorized"}), 403

            if request.method == "PUT":
                data = request.json
                data["updated_at"] = datetime.utcnow()
                self.collection.update_one({"_id": ObjectId(post_id)}, {"$set": data})
                return jsonify({"message": "Post updated successfully"}), 200

            self.collection.delete_one({"_id": ObjectId(post_id)})
            return jsonify({"message": "Post deleted successfully"}), 200

        @app.route("/posts/<string:post_id>/like", methods=["POST"])
        @login_required
        def like_post(user_id, post_id):
            post = self.collection.find_one({"_id": ObjectId(post_id)})
            if not post:
                return jsonify({"error": "Post not found"}), 404

            if user_id in post["likes"]:
                self.collection.update_one({"_id": ObjectId(post_id)}, {"$pull": {"likes": user_id}})
                return jsonify({"message": "Post unliked"}), 200

            self.collection.update_one({"_id": ObjectId(post_id)}, {"$addToSet": {"likes": user_id}})
            return jsonify({"message": "Post liked"}), 200

        @app.route("/posts/search", methods=["GET"])
        def search_posts():
            query = request.args.get("q", "")
            results = self.collection.find({"title": {"$regex": query, "$options": "i"}})
            posts = [{"_id": str(post["_id"]), "title": post["title"], "author": str(post["author"])} for post in results]
            return jsonify(posts), 200
        
        # Add the route to GET all posts
        @app.route("/posts", methods=["GET"])
        def get_all_posts():
            all_posts = list(self.collection.find())
            for post in all_posts:
                post["_id"] = str(post["_id"])
                post["author"] = str(post["author"])
            return jsonify(all_posts), 200
        
        @app.route("/analytics", methods=["GET"])
        @admin_required
        def analytics(user_id):
            total_posts = self.collection.count_documents({})
            average_views = self.collection.aggregate([
                {"$group": {"_id": None, "avg_views": {"$avg": "$views"}}}
            ])

            analytics_data = {
                "total_posts": total_posts,
                "average_views": average_views[0]["avg_views"]
            }
            return jsonify(analytics_data), 200
