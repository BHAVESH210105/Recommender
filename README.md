# 🎬 CineMatch - Movie Recommendation System

CineMatch is a content-based movie recommendation system built with Python, Scikit-learn, and Streamlit. It uses Natural Language Processing and Cosine Similarity to find movies similar to any chosen title based on genres, keywords, cast, crew, and storyline.

---

## ✨ Features

- **Content-Based Filtering**: Recommendations powered by CountVectorizer and Cosine Similarity across 4,800+ movies.
- **Cinematic UI**: Modern dark theme, glassmorphism, responsive posters fetched from TMDB CDN, and similarity scores.
- **⚡ Fallback Node (Guest Access)**: Instant access mode bypassing database auth — ideal for testing, demoing, and resilient deployments even when MongoDB is offline.
- **User Authentication**: Secure user registration and login backed by MongoDB Atlas with bcrypt password hashing.
- **Personal Watchlist**: Save and remove favorite movies (MongoDB persistent storage for registered users; session storage for Guest/Fallback mode).

---

## 🚀 Running Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables (Optional for MongoDB Atlas)**:
   Create a `.env` file in the root directory:
   ```env
   MONGO_URI=your_mongodb_connection_string
   MONGO_DB_NAME=cinematch
   ```
   *(Note: If `.env` is omitted, the app will automatically use the **Fallback Node** in guest mode.)*

4. **Launch the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push this repository to **GitHub**.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app**, select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. *(Optional)* Under **Advanced settings** -> **Secrets**, you can add your MongoDB credentials:
   ```toml
   MONGO_URI = "mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority"
   MONGO_DB_NAME = "cinematch"
   ```
5. Click **Deploy**!
6. If secrets are not provided, users can immediately explore the app using the **⚡ Fallback Node** on the login page!
