"""
Gmail Agent - Main Application Entry Point

Desktop application to run in background for fetching all emails.

1. Make desktop credentials on GCP and fix any configuration issues.
2. Get the APIs to develop the workflow for the app.
3. Develop the workflow to get the emails that were received in the last 24 hours or till some pivot point.
4. Figure out things we are going to configure on LangChain. (That is going to be the AI interface where emails are handled)
5. The flask app will help manage the information.

Need to build a frontend interface for getting the data.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from api.gmail_api import GmailAPI
from api.user_ops import check_if_user_exists, create_user, save_user_token, get_user_token
from config import Config


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route("/")
def home():
    print("Home route hit by %s", request.remote_addr)
    return "Hello, Flask logging!"

@app.route("/error")
def trigger_error():
    try:
        1 / 0
    except Exception as e:
        print("Error occurred: %s", e, exc_info=True)
        return "Something went wrong", 500
    
@app.route("/api/syncUser", methods=["POST"])
def sync_user():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        
        # TODO: Implement the logic to check if user exists.
        # TODO: Implement the logic to store the user in the database.
        if not check_if_user_exists(email):
            create_user(email)
            return jsonify({'success': True, 'message': 'User synced successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'User already exists!'}), 200
    except Exception as e:
        print(f"Error syncing user: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route("/api/setUserToken", methods=["POST"])
def set_user_token():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        # TODO: Implement the logic to get the user token from Gmail API.
        gmail_api = GmailAPI(email=email)
        
        
        if not email or not token_json:
            return jsonify({'error': 'Email and token JSON are required'}), 400
        
        save_user_token(email, token_json)
        return jsonify({'success': True, 'message': 'User token set successfully!'}), 200
    except Exception as e:
        print(f"Error setting user token: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/getUserEmails", methods=["GET"])
def get_user_emails():
    # TODO: Implement the logic to get the user token from the database or create a new token.
    # TODO: Implement the logic to get the user emails.
    # TODO: Classify them through the ML model.
    # TODO: Return the emails that are relevant to the user.
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        
        # Step 1: Create a new GmailAPI object, it handle the storage and retrieval of 
        # the user token as well.
        gmail_api = GmailAPI(email=email)
        
        # Get the updated tokens from the GmailAPI object.
        if not gmail_api.authenticate():
            return jsonify({'error': 'Failed to authenticate with Gmail API'}), 500
        
        # ------------------------------------------------------------------------------
        
        # Step 2: Get the user emails from the GmailAPI object.
        emails = gmail_api.get_emails()
        
        # Step 3: Classify the emails through the ML model.
        classified_emails = classify_emails(emails)
        
        # Step 4: Return the emails that are relevant to the user in a nice JSON format.
        return jsonify({'success': True, 'emails': emails}), 200
    except Exception as e:
        print(f"Error getting user emails: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=True)