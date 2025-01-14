from flask import request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from utils.auth import login_required


class CommentModel:
    def __init__(self, db):
        self.collection = db.comments

    def register_routes(self, app):
        @app.route("/posts/<string:post_id>/comments", methods=["POST"])
        @login_required
        def create_comment(user_id, post_id):
            data = request.json
            if not data.get("content"):
                return jsonify({"error": "Content is required"}), 400

            comment = {
                "post_id": ObjectId(post_id),
                "content": data["content"],
                "author": ObjectId(user_id),
                "parent_id": ObjectId(data.get("parent_id")) if data.get("parent_id") else None,
                "created_at": datetime.utcnow(),
            }

            self.collection.insert_one(comment)
            return jsonify({"message": "Comment added"}), 201

        @app.route("/posts/<string:post_id>/comments", methods=["GET"])
        def get_comments(post_id):
            comments = self.collection.find({"post_id": ObjectId(post_id)})
            response = []
            for comment in comments:
                comment["_id"] = str(comment["_id"])
                comment["author"] = str(comment["author"])
                comment["parent_id"] = str(comment["parent_id"]) if comment.get("parent_id") else None
                response.append(comment)
            return jsonify(response), 200
