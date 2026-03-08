from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
import sys

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all origins and methods
CORS(app, resources={r"/*": {"origins": "*"}})

# Read the MongoDB URI securely from Vercel's Environment Variables
MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
    # Log an error if URI is missing, but don't crash Vercel build
    sys.stderr.write("ERROR: MONGODB_URI environment variable not set!\n")
    # Provide dummy data if URI is missing to prevent full crash
    client = None
    db = None
    rob_db = None
else:
    try:
        # Attempt to connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client["JailbreakTracker"]
        rob_db = db["ActiveRobberies"]
        sys.stdout.write("MongoDB connected successfully.\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to connect to MongoDB: {e}\n")
        client = None
        db = None
        rob_db = None

# Ensure CORS headers are always added, including for OPTIONS preflight requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/getRobberies', methods=['GET', 'OPTIONS'])
def get_robberies():
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    # Check if MongoDB connection is valid
    if rob_db is None:
        return jsonify({"error": "Database connection failed or not configured."}), 500

    try:
        # Fetch all robberies. The _id must be removed because it's not JSON serializable
        # Sort by createdAt to get newest first
        robberies = list(rob_db.find({}, {"_id": 0}).sort("createdAt", -1))
        return jsonify(robberies), 200
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to fetch robberies: {e}\n")
        return jsonify({"error": f"Failed to fetch data: {e}"}), 500

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    return jsonify({"status": "Jailbreak Hub Vercel API is online!"}), 200

# Required for Vercel Serverless Functions to correctly route requests
def handler(event, context):
    return app(event, context)