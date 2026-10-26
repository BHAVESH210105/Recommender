import pandas as pd
import numpy as np
import ast
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("=" * 50)
print("CINEMATCH - MOVIE RECOMMENDATION SYSTEM")
print("=" * 50)

# --------------------------------------------------
# STEP 1: Define project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

movies_path = DATA_DIR / "tmdb_5000_movies.csv"
credits_path = DATA_DIR / "tmdb_5000_credits.csv"

# --------------------------------------------------
# STEP 2: Load datasets
# --------------------------------------------------

print("\nLoading datasets...")

if not movies_path.exists() or not credits_path.exists():
    raise FileNotFoundError(
        "Dataset files are missing. Check your data folder."
    )

movies = pd.read_csv(movies_path)
credits = pd.read_csv(credits_path)

print("Movies dataset:", movies.shape)
print("Credits dataset:", credits.shape)

# --------------------------------------------------
# STEP 3: Merge datasets
# --------------------------------------------------

movies = movies.merge(
    credits,
    left_on="id",
    right_on="movie_id",
    how="inner"
)

print("Merged dataset:", movies.shape)
print("Available columns:", movies.columns.tolist())

# --------------------------------------------------
# STEP 4: Select required columns
# --------------------------------------------------

required_columns = [
    "movie_id",
    "title_x",
    "genres",
    "keywords",
    "overview",
    "cast",
    "crew"
]

movies = movies[required_columns].copy()

movies.rename(
    columns={"title_x": "title"},
    inplace=True
)

# Remove missing and duplicate movie records
movies.dropna(subset=["title"], inplace=True)
movies.drop_duplicates(subset=["movie_id"], inplace=True)

# Fill missing text fields
for column in ["genres", "keywords", "overview", "cast", "crew"]:
    movies[column] = movies[column].fillna("[]")

# --------------------------------------------------
# STEP 5: Convert JSON-like columns into lists
# --------------------------------------------------

def convert_to_list(value):
    try:
        parsed = ast.literal_eval(value) if isinstance(value, str) else []
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []


def extract_names(value):
    return [
        item["name"].replace(" ", "")
        for item in convert_to_list(value)
        if isinstance(item, dict) and "name" in item
    ]


def extract_cast(value, limit=3):
    return extract_names(value)[:limit]


def extract_director(value):
    for person in convert_to_list(value):
        if (
            isinstance(person, dict)
            and person.get("job") == "Director"
        ):
            return person["name"].replace(" ", "")

    return ""


print("\nProcessing movie information...")

movies["genres"] = movies["genres"].apply(extract_names)
movies["keywords"] = movies["keywords"].apply(extract_names)
movies["cast"] = movies["cast"].apply(extract_cast)
movies["crew"] = movies["crew"].apply(extract_director)

# --------------------------------------------------
# STEP 6: Process movie descriptions
# --------------------------------------------------

movies["overview"] = movies["overview"].apply(
    lambda text: text.lower().split()
    if isinstance(text, str)
    else []
)

# Combine all movie features
movies["tags"] = (
    movies["genres"]
    + movies["keywords"]
    + movies["cast"]
    + movies["crew"].apply(
        lambda director: [director] if director else []
    )
    + movies["overview"]
)

# Convert lists into strings
movies["tags"] = movies["tags"].apply(
    lambda words: " ".join(words).lower()
)

# Keep only the columns needed by the recommendation engine
new_movies = movies[["movie_id", "title", "tags"]].copy()


# --------------------------------------------------
# Load and merge poster metadata
# --------------------------------------------------

posters_path = DATA_DIR / "movies_metadata.csv"

if not posters_path.exists():
    raise FileNotFoundError(
        f"Poster metadata file not found: {posters_path}"
    )

posters = pd.read_csv(
    posters_path,
    usecols=["id", "poster_path"],
    low_memory=False,
    on_bad_lines="skip"
)

# Convert poster IDs to numeric values
posters["id"] = pd.to_numeric(
    posters["id"], errors="coerce"
)

posters.dropna(subset=["id"], inplace=True)
posters["id"] = posters["id"].astype("int64")

# Remove duplicate IDs
posters.drop_duplicates(
    subset=["id"], inplace=True
)

# Convert movie IDs to numeric values
new_movies["movie_id"] = pd.to_numeric(
    new_movies["movie_id"], errors="coerce"
)

# Merge movie records with poster metadata
new_movies = new_movies.merge(
    posters[["id", "poster_path"]],
    left_on="movie_id",
    right_on="id",
    how="left",
    validate="many_to_one"
)

# Remove the extra ID column
new_movies.drop(columns=["id"], inplace=True)

# Keep only valid poster paths
new_movies["poster_path"] = new_movies["poster_path"].apply(
    lambda path: path.strip()
    if isinstance(path, str)
    and path.strip().startswith("/")
    else None
)

# Reset the index
new_movies.reset_index(drop=True, inplace=True)

# Display poster statistics
print(
    "Movies with valid posters:",
    new_movies["poster_path"].notna().sum()
)

print("\nSample poster records:")
print(
    new_movies[["title", "poster_path"]]
    .head(10)
    .to_string(index=False)
)
# DEBUG: Check poster paths
print("\n--- POSTER PATH DEBUG ---")

print(
    new_movies[["title", "poster_path"]]
    .head(20)
    .to_string(index=False)
)

print(
    "\nValid poster paths:",
    new_movies["poster_path"].notna().sum()
)

print(
    "Missing poster paths:",
    new_movies["poster_path"].isna().sum()
)

# --------------------------------------------------
# STEP 7: Convert text into numerical vectors
# --------------------------------------------------

print("Converting movie information into numerical vectors...")

cv = CountVectorizer(
    max_features=5000,
    stop_words="english"
)

vectors = cv.fit_transform(new_movies["tags"])

print("Vector matrix shape:", vectors.shape)

# --------------------------------------------------
# STEP 8: Calculate cosine similarity
# --------------------------------------------------

print("Calculating movie similarity...")

similarity = cosine_similarity(vectors, dense_output=False)

print("Similarity matrix shape:", similarity.shape)

# --------------------------------------------------
# STEP 9: Save the trained model data
# --------------------------------------------------

movie_file = MODEL_DIR / "movie_list.pkl"
similarity_file = MODEL_DIR / "similarity.pkl"
vectorizer_file = MODEL_DIR / "vectorizer.pkl"

with open(movie_file, "wb") as file:
    pickle.dump(new_movies, file)

with open(similarity_file, "wb") as file:
    pickle.dump(similarity, file)

with open(vectorizer_file, "wb") as file:
    pickle.dump(cv, file)

print("\n" + "=" * 50)
print("MODEL TRAINING COMPLETED SUCCESSFULLY!")
print("=" * 50)

print("Saved movie data:", movie_file)
print("Saved similarity matrix:", similarity_file)
print("Saved vectorizer:", vectorizer_file)