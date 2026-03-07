from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
# Enable CORS so your GitHub site can read it
CORS(app, resources={r"/*": {"origins": "*"}})

# It will read the URI securely from Vercel's environment variables
MONGO_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["JailbreakTracker"]
rob_db = db["ActiveRobberies"]

@app.route('/getRobberies', methods=['GET'])
def get_robberies():
    try:
        # Fetch all robberies. The _id must be removed because it's not JSON serializable
        robberies = list(rob_db.find({}, {"_id": 0}).sort("createdAt", -1))
        return jsonify(robberies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Vercel Serverless Functions
def handler(event, context):
    return app(event, context)