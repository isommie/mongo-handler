import os
import logging
import signal
import sys
from flask import Flask, request, jsonify
from pymongo import MongoClient, errors
# from token_auth import validate_token
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from bson import ObjectId
import json
import uuid

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Connection
mongo_url = os.environ.get('MONGO_URL')
if not mongo_url:
    raise ValueError("MONGO_URL environment variable is not set.")

try:
    # Create a MongoDB client with max pool size and wait queue timeout
    client = MongoClient(mongo_url, maxPoolSize=100, waitQueueTimeoutMS=3000)
    db = client.get_default_database()  # Get the default database
    shops_collection = db['shops']  # Collection name
    # shops_collection = db['shops']
    logger.info("MongoDB connection established successfully.")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    sys.exit(1)

# Set a reasonable max_workers value
MAX_WORKERS = 50  # Adjust this based on MongoDB capacity and server resources

@app.route('/data', methods=['GET'])
def process_data():
    """Endpoint to process MongoDB read/write requests from bots."""
    # token = request.headers.get('Authorization')
    # if not validate_token(token):
    #     return jsonify({'error': 'Unauthorized'}), 401

    # Generate a unique request_id
    # request_id = str(uuid.uuid4())

    # Parse the incoming JSON request
    request_data = request.json
    # request_data['request_id'] = request_id  # Add the request_id to the payload
    operation = request_data.get("operation", {})
    
    # Verify that the required fields are present
    if not operation:
        return jsonify({'error': 'no operation field found'}), 400
    
    # Determine operation type
    operation_type = operation.get("type")
    collection_name = operation.get("collection_name", "bots")
    query = operation.get("query", {})
    bulk = operation.get("bulk", False)
    update_data = operation.get("update") if operation_type == "write" else None
    
    try:
        if operation_type == "read":
            response = handle_read_operation(collection_name, query, bulk)
        elif operation_type == "write":
            response = handle_write_operation(collection_name, query, update_data)
        else:
            return jsonify({'error': 'Invalid operation type'}), 400
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        response = {"status": "error", "message": str(e)}

    # Return the response
    return jsonify(response), 200



def process_single_request(data):
    """Process a single request to interact with MongoDB."""
    operation = data.get('operation', {})
    collection_name = operation.get('shops_collection_name', 'bots')
    query = operation.get('query', {})

    response = {}

    try:
        if operation.get('type') == 'read':
            response = handle_read_operation(collection_name, query, operation.get('bulk', False))
        elif operation.get('type') == 'write':
            update = operation.get('update')
            response = handle_write_operation(collection_name, query, update)
    except Exception as e:
        logger.error(f"Error processing request {data.get('request_id')}: {str(e)}")
        response = {"status": "error", "message": str(e)}

    return response


def handle_read_operation(collection_name, query, bulk):
    """Handle read operations for MongoDB."""
    collection = db[collection_name]
    if "_id" in query:
        query["_id"] = ObjectId(query["_id"]["$oid"])  # Convert _id to ObjectId
    
    if bulk:
        documents = list(collection.find(query))
    else:
        documents = [collection.find_one(query)]
    
    # Format documents to be JSON serializable
    documents = [convert_object_ids_and_dates(doc) for doc in documents if doc]
    
    return {
        "status": "success",
        "operation": "read",
        "data": documents if bulk else (documents[0] if documents else {})
    }

def handle_write_operation(collection_name, query, update_data):
    """Handle write operations for MongoDB."""
    collection = db[collection_name]
    if "_id" in query:
        query["_id"] = ObjectId(query["_id"]["$oid"])  # Convert _id to ObjectId

    # Update the document
    result = collection.update_one(query, {"$set": update_data}) if update_data else None
    return {
        "status": "success" if result and result.modified_count > 0 else "no_change",
        "operation": "write",
        "matched_count": result.matched_count if result else 0,
        "modified_count": result.modified_count if result else 0
    }


def convert_object_ids_and_dates(document):
    """ Recursively convert ObjectIds and datetime objects to JSON serializable formats. """
    if isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, ObjectId):
                document[key] = str(value)
            elif isinstance(value, datetime):
                document[key] = value.isoformat()
            elif isinstance(value, dict):
                document[key] = convert_object_ids_and_dates(value)
            elif isinstance(value, list):
                document[key] = [convert_object_ids_and_dates(item) if isinstance(item, (dict, ObjectId, datetime)) else item for item in value]
    elif isinstance(document, list):
        document = [convert_object_ids_and_dates(item) if isinstance(item, (dict, ObjectId, datetime)) else item for item in document]
    return document

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to monitor the status of the application."""
    try:
        client.admin.command('ping')  # Check MongoDB connection
        return jsonify({"status": "up"}), 200
    except errors.PyMongoError:
        return jsonify({"status": "down"}), 500

def signal_handler(sig, frame):
    """Handle shutdown signals for graceful shutdown."""
    client.close()  # Close MongoDB connection
    logger.info("Shutting down gracefully...")
    sys.exit(0)

# Set up signal handling for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
