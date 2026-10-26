import pickle
from pathlib import Path

import pandas as pd
import requests

# Project paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "movie_list.pkl"

# Load the movie dataset used by CineMatch
with open(MODEL_PATH, "rb") as file:
    movies = pickle.load(file)

print("\n========== CINEMATCH POSTER DIAGNOSTICS ==========")

print("\nDataset shape:", movies.shape)
print("\nAvailable columns:")
print(movies.columns.tolist())

# Check whether poster_path exists
if "poster_path" not in movies.columns:
    print("\nERROR: poster_path column is missing!")
    raise SystemExit

# Check missing and empty paths
paths = movies["poster_path"]

missing = paths.isna() | paths.astype(str).str.strip().isin(
    ["", "None", "nan", "NaN"]
)

print("\nTotal movies:", len(movies))
print("Missing poster paths:", int(missing.sum()))
print("Available poster paths:", int((~missing).sum()))

print("\n========== SAMPLE POSTER PATHS ==========")

for _, row in movies.head(15).iterrows():
    print(f"{row.get('title', 'Unknown')}: {row['poster_path']}")

print("\n========== TESTING POSTER URLS ==========")

# Test a few non-empty paths
tested = 0

for _, row in movies.loc[~missing].head(10).iterrows():
    title = row.get("title", "Unknown")
    path = str(row["poster_path"]).strip()

    # Check whether the dataset contains a relative TMDB path
    if not path.startswith("/") or path.count("/") < 1:
        print(f"\nINVALID PATH: {title} -> {path}")
        continue

    # Construct the image URL
    url = f"https://image.tmdb.org/t/p/w500{path}"

    try:
        response = requests.get(
            url,
            timeout=15,
            stream=True,
            headers={"User-Agent": "CineMatch/1.0"},
        )

        content_type = response.headers.get("Content-Type", "")

        print(f"\nMovie: {title}")
        print("URL:", url)
        print("HTTP status:", response.status_code)
        print("Content-Type:", content_type)

        if response.status_code == 200 and content_type.startswith("image/"):
            print("RESULT: Poster URL works")
        elif response.status_code == 404:
            print("RESULT: Image not found at this URL")
        else:
            print("RESULT: Check status code and response headers")

        response.close()
        tested += 1

    except requests.RequestException as error:
        print(f"\nREQUEST ERROR for {title}: {error}")

    if tested >= 5:
        break

print("\n========== DIAGNOSTICS COMPLETE ==========")