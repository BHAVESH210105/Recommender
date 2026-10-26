
import os
import pickle
import shutil
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# -------------------------------
# CONFIGURATION
# -------------------------------
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
MOVIE_FILE = MODEL_DIR / "movie_list.pkl"
BACKUP_FILE = MODEL_DIR / "movie_list_backup.pkl"

IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

if not API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env")

if not MOVIE_FILE.exists():
    raise FileNotFoundError(f"Movie file not found: {MOVIE_FILE}")

# -------------------------------
# LOAD DATA
# -------------------------------
with open(MOVIE_FILE, "rb") as file:
    movies = pickle.load(file)

if not isinstance(movies, pd.DataFrame):
    raise TypeError("movie_list.pkl does not contain a pandas DataFrame.")

required_columns = {"title", "poster_path"}

if not required_columns.issubset(movies.columns):
    raise ValueError(
        f"Required columns missing. Available: {movies.columns.tolist()}"
    )

# Create a backup before making changes.
if not BACKUP_FILE.exists():
    shutil.copy2(MOVIE_FILE, BACKUP_FILE)
    print(f"Backup created: {BACKUP_FILE}")
else:
    print(f"Existing backup preserved: {BACKUP_FILE}")

session = requests.Session()
session.headers.update({"User-Agent": "CineMatch/1.0"})

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def poster_is_valid(poster_path):
    """Check whether a TMDB poster path returns an image."""
    if not isinstance(poster_path, str):
        return False

    poster_path = poster_path.strip()

    if not poster_path.startswith("/"):
        return False

    try:
        response = session.get(
            IMAGE_BASE_URL + poster_path,
            timeout=15,
            stream=True,
        )

        valid = (
            response.status_code == 200
            and response.headers.get("Content-Type", "").startswith("image/")
        )

        response.close()
        return valid

    except requests.RequestException:
        return False


def search_tmdb(title):
    """Find a likely movie match and return its poster path."""
    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": API_KEY,
        "query": title,
        "include_adult": "false",
    }

    response = session.get(url, params=params, timeout=20)
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    # Prefer an exact title match when available.
    normalized_title = title.strip().casefold()

    exact_matches = [
        result for result in results
        if result.get("title", "").strip().casefold() == normalized_title
    ]

    candidates = exact_matches if exact_matches else results

    # Try the most relevant candidates first.
    for result in candidates[:5]:
        poster_path = result.get("poster_path")

        if poster_path and poster_is_valid(poster_path):
            return poster_path

    return None


# -------------------------------
# REPAIR POSTER PATHS
# -------------------------------
total = len(movies)
repaired = 0
failed = 0
already_valid = 0

print(f"\nTotal movies: {total}")
print("Checking poster paths...\n")

for index in movies.index:
    title = movies.at[index, "title"]
    current_path = movies.at[index, "poster_path"]

    if not isinstance(title, str) or not title.strip():
        failed += 1
        continue

    # Keep working paths unchanged.
    if poster_is_valid(current_path):
        already_valid += 1
        continue

    try:
        new_path = search_tmdb(title)

        if new_path:
            movies.at[index, "poster_path"] = new_path
            repaired += 1
            print(f"[FIXED] {title}: {new_path}")
        else:
            failed += 1
            print(f"[NOT FOUND] {title}")

        # Avoid sending requests too quickly.
        time.sleep(0.15)

    except requests.RequestException as error:
        failed += 1
        print(f"[ERROR] {title}: {error}")

    if (repaired + failed + already_valid) % 100 == 0:
        print(
            f"Progress: {repaired + failed + already_valid}/{total}"
        )

# -------------------------------
# SAVE UPDATED DATA
# -------------------------------
TEMP_FILE = MODEL_DIR / "movie_list_repaired.tmp"

with open(TEMP_FILE, "wb") as file:
    pickle.dump(movies, file, protocol=pickle.HIGHEST_PROTOCOL)

# Replace the original only after writing the updated file.
TEMP_FILE.replace(MOVIE_FILE)

print("\n========== SUMMARY ==========")
print("Total movies:", total)
print("Already valid:", already_valid)
print("Repaired:", repaired)
print("Unresolved or errors:", failed)
print("Updated file:", MOVIE_FILE)
print("Backup:", BACKUP_FILE)
print("\nPoster repair finished.")

