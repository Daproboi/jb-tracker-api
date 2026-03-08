from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
import sys

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- MongoDB Connection Setup (Vercel Optimized) ---
MONGO_URI = os.environ.get("MONGODB_URI")
client = None
db = None
rob_db = None

if not MONGO_URI:
    sys.stderr.write("ERROR: MONGODB_URI environment variable not set on Vercel!\n")
else:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, maxPoolSize=1) # Added maxPoolSize for serverless
        db = client["JailbreakTracker"]
        rob_db = db["ActiveRobberies"]
        client.admin.command('ping') 
        sys.stdout.write("MongoDB connected successfully to Vercel.\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to connect to MongoDB on Vercel: {e}\n")
        client = None

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/getRobberies', methods=['GET', 'OPTIONS'])
def get_robberies():
    if request.method == 'OPTIONS': return jsonify({}), 200
    
    if rob_db is None:
        sys.stderr.write("ERROR: getRobberies called but MongoDB client is not initialized.\n")
        return jsonify({"error": "Database connection not available."}), 500

    try:
        robberies = list(rob_db.find({}, {"_id": 0}).sort("createdAt", -1))
        return jsonify(robberies), 200
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to fetch robberies: {e}\n")
        return jsonify({"error": f"Failed to fetch data: {e}"}), 500

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    if request.method == 'OPTIONS': return jsonify({}), 200
    if rob_db is None:
        return jsonify({"status": "Jailbreak Hub Vercel API is online (but database is offline)."}), 200
    return jsonify({"status": "Jailbreak Hub Vercel API is online and connected to DB!"}), 200

# Vercel requires a WSGI application for Flask. This is the standard way to expose it.
# We are renaming 'app' to 'wsgi_app' internally for Vercel.
wsgi_app = app