from auth import get_database

username = "R Prashanth"
movie_title = "Test Movie"

try:
    db = get_database()
    watchlist = db["watchlist"]

    result = watchlist.insert_one({
        "username": username,
        "movie_title": movie_title
    })

    print("Movie inserted successfully!")
    print("Inserted ID:", result.inserted_id)

    saved_movie = watchlist.find_one({
        "_id": result.inserted_id
    })

    print("Saved document:", saved_movie)

except Exception as e:
    print("ERROR:", repr(e))