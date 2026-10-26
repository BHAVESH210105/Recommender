
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env")

# Search for Avatar (2009)
url = "https://api.themoviedb.org/3/search/movie"

params = {
    "api_key": API_KEY,
    "query": "Avatar",
    "year": 2009,
}

try:
    response = requests.get(url, params=params, timeout=20)

    print("TMDB API status:", response.status_code)

    if response.status_code != 200:
        print("API error:", response.text)
        raise SystemExit

    results = response.json().get("results", [])

    if not results:
        print("No matching movie found.")
        raise SystemExit

    movie = results[0]
    poster_path = movie.get("poster_path")

    print("Movie:", movie["title"])
    print("TMDB ID:", movie["id"])
    print("Poster path:", poster_path)

    if not poster_path:
        print("This movie has no poster path.")
        raise SystemExit

    poster_url = (
        "https://image.tmdb.org/t/p/w500" + poster_path
    )

    print("Poster URL:", poster_url)

    image_response = requests.get(poster_url, timeout=20)

    print("Poster HTTP status:", image_response.status_code)
    print("Content-Type:", image_response.headers.get("Content-Type"))

    if (
        image_response.status_code == 200
        and image_response.headers.get("Content-Type", "").startswith("image/")
    ):
        print("SUCCESS: TMDB poster is accessible!")
    else:
        print("The poster URL did not return a valid image.")

except requests.RequestException as error:
    print("Network error:", error)
