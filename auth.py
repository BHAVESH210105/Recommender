import os
import streamlit as st
import bcrypt

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load environment variables
load_dotenv()


def get_mongo_uri():
    """Retrieve MongoDB URI from Streamlit secrets or environment variables."""
    try:
        if hasattr(st, "secrets") and "MONGO_URI" in st.secrets:
            return st.secrets["MONGO_URI"]
    except Exception:
        pass
    return os.getenv("MONGO_URI")


def get_db_name():
    """Retrieve MongoDB database name."""
    try:
        if hasattr(st, "secrets") and "MONGO_DB_NAME" in st.secrets:
            return st.secrets["MONGO_DB_NAME"]
    except Exception:
        pass
    return os.getenv("MONGO_DB_NAME", "cinematch")


@st.cache_resource
def get_database():
    """Connect to MongoDB Atlas with timeout and graceful error handling."""
    mongo_uri = get_mongo_uri()
    if not mongo_uri:
        return None

    try:
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=4000
        )
        # Verify connection
        client.admin.command("ping")
        return client[get_db_name()]
    except Exception:
        return None


def register_user(username, email, password):
    """Register a new user in MongoDB."""
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    try:
        db = get_database()
        if db is None:
            return False, "Database connection unavailable. Please use the Fallback Node (Guest Mode)."

        users = db["users"]

        # Check for an existing username or email
        existing_user = users.find_one({
            "$or": [
                {"username": username},
                {"email": email}
            ]
        })

        if existing_user:
            return False, "Username or email already exists."

        # Hash the password before storing it
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        users.insert_one({
            "username": username,
            "email": email,
            "password_hash": password_hash
        })

        return True, "Account created successfully!"

    except (PyMongoError, Exception):
        return False, "Database error. Please try again or use the Fallback Node."


def login_user(username, password):
    """Authenticate an existing user."""
    username = username.strip()

    if not username or not password:
        return False, None, "Please enter both username and password."

    try:
        db = get_database()
        if db is None:
            return False, None, "Database connection unavailable. Please use the Fallback Node (Guest Mode)."

        user = db["users"].find_one({
            "username": username
        })

        if user is None:
            return False, None, "Invalid username or password."

        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if not password_matches:
            return False, None, "Invalid username or password."

        return True, user, "Login successful!"

    except (PyMongoError, Exception):
        return False, None, "Database error. Please try again or use the Fallback Node."


# ------------------------------------------
# WATCHLIST FUNCTIONS (Supports MongoDB & Fallback Session)
# ------------------------------------------

def _init_guest_watchlist():
    if "guest_watchlist" not in st.session_state:
        st.session_state.guest_watchlist = []


def add_to_watchlist(username, movie_title):
    """Add a movie to the user's watchlist (MongoDB or session fallback)."""
    _init_guest_watchlist()

    # Fallback mode for Guest or when DB is offline
    if username == "Guest" or get_database() is None:
        if movie_title in st.session_state.guest_watchlist:
            return False, "This movie is already in your watchlist."
        st.session_state.guest_watchlist.append(movie_title)
        return True, "Movie added to your watchlist (session mode)!"

    try:
        db = get_database()
        watchlist = db["watchlist"]

        existing = watchlist.find_one({
            "username": username,
            "movie_title": movie_title
        })

        if existing:
            return False, "This movie is already in your watchlist."

        watchlist.insert_one({
            "username": username,
            "movie_title": movie_title
        })

        return True, "Movie added to your watchlist!"

    except (PyMongoError, Exception):
        # Graceful fallback to session watchlist if MongoDB write fails
        if movie_title not in st.session_state.guest_watchlist:
            st.session_state.guest_watchlist.append(movie_title)
            return True, "Saved to session watchlist (offline fallback)!"
        return False, "Database error. Please try again."


def get_watchlist(username):
    """Retrieve a user's watchlist."""
    _init_guest_watchlist()

    if username == "Guest" or get_database() is None:
        return [{"movie_title": title} for title in st.session_state.guest_watchlist]

    try:
        db = get_database()
        return list(
            db["watchlist"].find(
                {"username": username},
                {"_id": 0, "movie_title": 1}
            )
        )
    except (PyMongoError, Exception):
        return [{"movie_title": title} for title in st.session_state.guest_watchlist]


def remove_from_watchlist(username, movie_title):
    """Remove a movie from the user's watchlist."""
    _init_guest_watchlist()

    if username == "Guest" or get_database() is None:
        if movie_title in st.session_state.guest_watchlist:
            st.session_state.guest_watchlist.remove(movie_title)
            return True, "Movie removed from your watchlist."
        return False, "Movie was not found in your watchlist."

    try:
        db = get_database()
        result = db["watchlist"].delete_one({
            "username": username,
            "movie_title": movie_title
        })

        if result.deleted_count:
            return True, "Movie removed from your watchlist."

        return False, "Movie was not found in your watchlist."

    except (PyMongoError, Exception):
        if movie_title in st.session_state.guest_watchlist:
            st.session_state.guest_watchlist.remove(movie_title)
            return True, "Movie removed from session watchlist."
        return False, "Database error. Please try again."