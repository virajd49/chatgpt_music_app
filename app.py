from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"

client = MongoClient("mongodb+srv://viraj_deshpande:Mongodb!49@cluster0.0d7upzm.mongodb.net/music_app_v1?retryWrites=true&w=majority")
db = client.get_database("music_app_v1")
users = db.users

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("playlist"))
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    username = request.json.get("username")
    password = request.json.get("password")
    confirm_password = request.json.get("confirm_password")

    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match"})

    existing_user = users.find_one({"email": email})

    if existing_user:
        return jsonify({"status": "error", "message": "Email already registered"})

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    users.insert_one({"email": email, "username": username, "password": hashed_password})

    return jsonify({"status": "success"})


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")
    user = users.find_one({"email": email})

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        session["user"] = str(user["_id"])
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error"})


@app.route("/playlist")
def playlist():
    if "user" not in session:
        return redirect(url_for("index"))

    user_id = ObjectId(session["user"])
    user = users.find_one({"_id": user_id})
    saved_playlist = user.get("playlist", [])

    return render_template("playlist.html", username=user["username"], saved_playlist=saved_playlist)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

# Add a new route for saving the playlist
@app.route("/save-playlist", methods=["POST"])
def save_playlist():
    if "user" not in session:
        return jsonify({"status": "error", "message": "User not logged in"})

    playlist = request.json["playlist"]
    user_id = ObjectId(session["user"])
    users.update_one({"_id": user_id}, {"$set": {"playlist": playlist}})

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
