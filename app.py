from flask import Flask, jsonify
from flask_pymongo import PyMongo, ObjectId
from flask_login import LoginManager
from models.accounts import AccountModel
from models.articles import ArticleModel
from models.responses import ResponseModel
from models.tags import TagModel
from utils.file_handler import initialize_file_uploads

app = Flask(__name__)

# Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/blog_platform"
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["SECRET_KEY"] = "your_secret_key"

# MongoDB
mongo = PyMongo(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Initialize models
account_model = AccountModel(mongo.db)
article_model = ArticleModel(mongo.db)
response_model = ResponseModel(mongo.db)
tag_model = TagModel(mongo.db)

# Setup file uploads
initialize_file_uploads(app)

# Register routes
account_model.register_routes(app)
article_model.register_routes(app)
response_model.register_routes(app)
tag_model.register_routes(app)

# Flask-Login user loader
@login_manager.user_loader
def load_account(account_id):
    account = mongo.db.users.find_one({"_id": ObjectId(account_id)})
    if account:
        return AccountModel(account["_id"], account["username"])
    return None

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Blog Platform API!"})

if __name__ == "__main__":
    app.run(debug=True)
