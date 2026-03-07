from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
# Enable CORS so your GitHub site can read it securely
CORS(app, resources={r"/*": {"origins": "*"}})

# Read the MongoDB URI from Vercel's Environment Variables
MONGO_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["JailbreakTracker"]
rob_db = db["ActiveRobberies"]

@app.route('/')
def home():
    return jsonify({"status": "Vercel API is online!"}), 200

@app.route('/getRobberies', methods=['GET', 'OPTIONS'])
def get_robberies():
    try:
        # Fetch all robberies. The _id must be removed because it's not JSON serializable
        robberies = list(rob_db.find({}, {"_id": 0}).sort("createdAt", -1))
        return jsonify(robberies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500