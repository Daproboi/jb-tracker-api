from flask import Flask, jsonify, request
from flask_cors import CORS # This is crucial for Vercel
from pymongo import MongoClient
import os

app = Flask(__name__)
# Enable CORS for all origins (your GitHub Pages site)
CORS(app, resources={r"/*": {"origins": "*"}})

# Read the MongoDB URI securely from Vercel's Environment Variables
MONGO_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["JailbreakTracker"]
rob_db = db["ActiveRobberies"]

# Add a global after_request to ensure CORS headers are always present
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/getRobberies', methods=['GET', 'OPTIONS'])
def get_robberies():
    if request.method == 'OPTIONS':
        # Respond to preflight requests (handled by CORS(app) primarily)
        return jsonify({}), 200
    
    try:
        # Fetch all robberies. The _id must be removed because it's not JSON serializable
        robberies = list(rob_db.find({}, {"_id": 0}).sort("createdAt", -1))
        return jsonify(robberies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Vercel Serverless Functions
def handler(event, context):
    return app(event, context)