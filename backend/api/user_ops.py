from datetime import datetime
from typing import Optional, Dict, Any
import json

from model import SessionLocal, User

def check_if_user_exists(email: str) -> bool:
    """
    Check if user exists in the database.
    Returns True if user exists, False otherwise.
    """
    with SessionLocal() as session:
        return session.query(User).filter(User.email == email).first() is not None
    
def store_user(email: str, username: str) -> dict:
    """
    Save or update user's token JSON.
    Returns a dict of the user data.
    """
    with SessionLocal() as session:
        user = session.query(User).filter(User.email == email).first()
        
def store_user_token(email: str, username: str, token_json: Dict[str, Any]) -> dict:
    """
    Save or update user's token JSON.
    Returns a dict of the user data.
    """
    with SessionLocal() as session:
        # Check if user exists
        user = session.query(User).filter(User.email == email).first()
        
        if user:
            # Update existing user
            user.username = username
            user.token_json = token_json
            user.updated_at = datetime.now()
        else:
            # Create new user
            user = User(
                email=email,
                username=username,
                token_json=token_json,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(user)
        
        session.commit()
        session.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "token_json": user.token_json,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

def get_user_token(email: str) -> Optional[Dict[str, Any]]:
    """Return the token JSON for an email, or None if not found."""
    with SessionLocal() as session:
        user = session.query(User).filter(User.email == email).first()
        return user.token_json if user else None


if __name__ == "__main__":
    # Example token JSON (this would come from Google OAuth in real use)
    example_token = {
        "token": "ya29.example_access_token",
        "refresh_token": "1//example_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "example_client_id.apps.googleusercontent.com",
        "client_secret": "example_client_secret",
        "scopes": [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ]
    }
    
    print("TESTING store_user_token:")
    result = store_user_token(
        email="alice@example.com",
        username="alice",
        token_json=example_token
    )
    print(f"  Stored: {result['email']}, username: {result['username']}")
    
    print("\nTESTING get_user_token:")
    token = get_user_token("alice@example.com")
    print(f"  Retrieved token for alice@example.com: {token is not None}")