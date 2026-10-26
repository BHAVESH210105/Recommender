import pickle
from pathlib import Path

import pandas as pd
import streamlit as st

from auth import (
    add_to_watchlist,
    get_watchlist,
    login_user,
    register_user,
    remove_from_watchlist,
)


# ------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------
st.set_page_config(
    page_title="CineMatch | Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"


# ------------------------------------------
# CINEMATIC FRONTEND STYLING
# Background images are loaded from Unsplash Source URLs.
# Core recommendation/authentication/watchlist logic is unchanged.
# ------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    :root {
        --cm-purple: #8b5cf6;
        --cm-pink: #ec4899;
        --cm-panel: rgba(17, 17, 30, 0.86);
        --cm-border: rgba(255,255,255,0.13);
        --cm-muted: #c4c1d4;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        color: #f8f7ff;
        background:
            linear-gradient(115deg, rgba(7, 7, 18, 0.96) 0%,
                rgba(15, 8, 31, 0.88) 48%, rgba(21, 8, 26, 0.88) 100%),
            url("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=2400&q=85")
            center / cover fixed;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(13, 10, 27, 0.98), rgba(28, 10, 38, 0.97)),
            url("https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=1000&q=80")
            center / cover;
        border-right: 1px solid rgba(168, 85, 247, 0.28);
    }

    [data-testid="stSidebar"] * {
        color: #f8f7ff;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.035em;
        color: #ffffff;
    }

    h1 {
        font-weight: 800 !important;
        line-height: 1.08 !important;
    }

    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
        color: #e3dfef;
    }

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }

    .cm-brand {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 8px 15px;
        margin-bottom: 18px;
        border: 1px solid rgba(236, 72, 153, 0.35);
        border-radius: 999px;
        background: rgba(17, 10, 30, 0.75);
        color: #f5d0fe;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 0.78rem;
    }

    .cm-hero {
        padding: clamp(26px, 5vw, 62px);
        border: 1px solid var(--cm-border);
        border-radius: 28px;
        background:
            linear-gradient(105deg, rgba(10, 8, 24, 0.96) 0%,
                rgba(23, 10, 40, 0.82) 52%, rgba(25, 8, 25, 0.52) 100%),
            url("https://images.unsplash.com/photo-1440404653325-ab127d49abd1?auto=format&fit=crop&w=1800&q=85")
            center / cover;
        box-shadow: 0 24px 80px rgba(0,0,0,0.35);
        margin-bottom: 24px;
    }

    .cm-hero h1 {
        font-size: clamp(2.5rem, 6vw, 4.8rem);
        margin: 0.1rem 0 0.8rem 0;
    }

    .cm-gradient-text {
        background: linear-gradient(90deg, #c4b5fd, #f0abfc, #f9a8d4);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .cm-hero p {
        color: #e4dff1;
        max-width: 720px;
        font-size: 1.08rem;
        line-height: 1.75;
    }

    .cm-section-label {
        color: #d8b4fe;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.76rem;
        font-weight: 700;
    }

    .cm-panel {
        background: var(--cm-panel);
        border: 1px solid var(--cm-border);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 14px 40px rgba(0,0,0,0.18);
        backdrop-filter: blur(16px);
    }

    .cm-feature {
        min-height: 150px;
        background: linear-gradient(145deg, rgba(139,92,246,0.17), rgba(236,72,153,0.08));
        border: 1px solid rgba(196,181,253,0.18);
        border-radius: 20px;
        padding: 22px;
    }

    .cm-feature-icon {
        font-size: 1.8rem;
        margin-bottom: 10px;
    }

    .cm-feature-title {
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .cm-feature-copy {
        color: #c9c3dc;
        font-size: 0.91rem;
        line-height: 1.5;
    }

    .cm-auth-hero {
        padding: 30px;
        min-height: 260px;
        border-radius: 26px;
        border: 1px solid rgba(255,255,255,0.16);
        background:
            linear-gradient(110deg, rgba(8,7,19,0.95), rgba(30,10,45,0.73)),
            url("https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=1600&q=85")
            center / cover;
        margin-bottom: 20px;
    }

    .cm-auth-hero h1 {
        font-size: clamp(2.2rem, 5vw, 3.7rem);
        margin-bottom: 0.6rem;
    }

    .cm-auth-hero p {
        max-width: 650px;
        color: #ddd6ed;
        line-height: 1.7;
    }

    div[data-testid="stMetric"] {
        background: rgba(20, 14, 35, 0.78);
        border: 1px solid rgba(196,181,253,0.18);
        border-radius: 18px;
        padding: 18px 20px;
        backdrop-filter: blur(12px);
    }

    div[data-testid="stMetricLabel"] {
        color: #c4b5fd !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif;
    }

    .stButton > button {
        border: 1px solid rgba(216,180,254,0.35);
        border-radius: 12px;
        padding: 0.62rem 1.1rem;
        color: #ffffff;
        font-weight: 700;
        background: linear-gradient(100deg, #7c3aed, #db2777);
        box-shadow: 0 8px 22px rgba(124,58,237,0.18);
        transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        filter: brightness(1.1);
        border-color: rgba(255,255,255,0.5);
        box-shadow: 0 12px 28px rgba(219,39,119,0.24);
        color: #ffffff;
    }

    .stButton > button:focus {
        outline: 2px solid #c4b5fd;
        outline-offset: 2px;
    }

    .stTextInput input, .stSelectbox [data-baseweb="select"],
    .stTextArea textarea {
        background: rgba(12, 10, 24, 0.82) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border-color: rgba(196,181,253,0.3) !important;
    }

    [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    [data-baseweb="tab"] {
        background: rgba(20,14,35,0.7);
        border-radius: 12px 12px 0 0;
        padding: 10px 18px;
    }

    [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(139,92,246,0.24);
    }

    [data-testid="stAlert"] {
        background: rgba(25, 17, 42, 0.9);
        border-radius: 14px;
        border: 1px solid rgba(196,181,253,0.2);
    }

    .cm-movie-card {
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 20px;
        background: linear-gradient(120deg, rgba(18,14,32,0.92), rgba(35,13,43,0.82));
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
    }

    .cm-footer {
        text-align: center;
        color: #a8a1bc;
        font-size: 0.82rem;
        padding: 24px 0 6px 0;
    }

    hr {
        border-color: rgba(255,255,255,0.12) !important;
    }

    /* Premium purple polish: navigation, controls, cards and images */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 0.45rem 0.65rem;
        border-radius: 10px;
        transition: background 180ms ease, transform 180ms ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(139, 92, 246, 0.16);
        transform: translateX(3px);
    }

    [data-testid="stImage"] img {
        border-radius: 14px;
        border: 1px solid rgba(216, 180, 254, 0.22);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.32);
        transition: transform 220ms ease, box-shadow 220ms ease;
    }
    [data-testid="stImage"] img:hover {
        transform: translateY(-4px) scale(1.015);
        box-shadow: 0 18px 36px rgba(139, 92, 246, 0.24);
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }
    [data-baseweb="select"] > div:focus-within {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }

    .stButton > button:active {
        transform: scale(0.985);
    }
    .stDownloadButton > button {
        border-radius: 12px;
        border: 1px solid rgba(196, 181, 253, 0.3);
        background: rgba(139, 92, 246, 0.13);
        color: #f8f7ff;
    }

    [data-testid="stExpander"] {
        background: rgba(17, 17, 30, 0.62);
        border: 1px solid rgba(196, 181, 253, 0.18);
        border-radius: 14px;
    }
    [data-testid="stForm"] {
        background: rgba(17, 17, 30, 0.45);
        border: 1px solid rgba(196, 181, 253, 0.15);
        border-radius: 18px;
        padding: 18px;
    }
    ::selection {
        background: rgba(168, 85, 247, 0.45);
        color: white;
    }
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #0b0b12; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #8b5cf6, #db2777);
        border-radius: 999px;
        border: 2px solid #0b0b12;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            transition-duration: 0.01ms !important;
            animation-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }

    @media (max-width: 768px) {
        .block-container { padding-top: 1.2rem; }
        .cm-hero { border-radius: 20px; padding: 24px; }
        .cm-auth-hero { padding: 22px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------
# LOAD TRAINED MODEL
# ------------------------------------------
@st.cache_resource
def load_model():
    import gzip

    with open(MODEL_DIR / "movie_list.pkl", "rb") as file:
        movies = pickle.load(file)

    similarity_gz = MODEL_DIR / "similarity.pkl.gz"
    similarity_raw = MODEL_DIR / "similarity.pkl"

    if similarity_gz.exists():
        with gzip.open(similarity_gz, "rb") as file:
            similarity = pickle.load(file)
    elif similarity_raw.exists():
        with open(similarity_raw, "rb") as file:
            similarity = pickle.load(file)
    else:
        raise FileNotFoundError(
            "Trained model files were not found. "
            "Please ensure models/movie_list.pkl and models/similarity.pkl.gz are present."
        )

    return movies, similarity


try:
    movies, similarity = load_model()
except FileNotFoundError as err:
    st.error(str(err))
    st.stop()


# ------------------------------------------
# RECOMMENDATION FUNCTION — UNCHANGED
# ------------------------------------------
def recommend(movie_title, number_of_recommendations=5):
    matches = movies[
        movies["title"].str.casefold() == movie_title.casefold()
    ]

    if matches.empty:
        return []

    movie_index = matches.index[0]
    scores = similarity.getrow(movie_index).toarray().ravel()
    ranked_indices = scores.argsort()[::-1]
    recommendations = []

    for index in ranked_indices:
        if index == movie_index:
            continue

        recommendations.append(
            {
                "title": movies.iloc[index]["title"],
                "similarity": round(float(scores[index]), 3),
                "poster_path": movies.iloc[index].get("poster_path"),
            }
        )

        if len(recommendations) == number_of_recommendations:
            break

    return recommendations


# ------------------------------------------
# SESSION STATE
# ------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "is_guest" not in st.session_state:
    st.session_state.is_guest = False

if "guest_watchlist" not in st.session_state:
    st.session_state.guest_watchlist = []


# ------------------------------------------
# LOGIN / REGISTRATION & FALLBACK NODE
# ------------------------------------------
if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="cm-auth-hero">
            <div class="cm-brand">🎬 CINEMATCH • YOUR NEXT FAVORITE</div>
            <h1>Every story starts<br>with <span class="cm-gradient-text">a recommendation.</span></h1>
            <p>Discover your next movie obsession. Explore titles with similar stories,
            genres, actors, directors, and cinematic vibes — all in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab, fallback_tab = st.tabs([
        "🔐  Login",
        "✨  Create account",
        "⚡  Fallback Node (Guest)"
    ])

    with login_tab:
        st.markdown('<div class="cm-panel">', unsafe_allow_html=True)
        st.subheader("Welcome back")
        st.caption("Sign in to continue your movie journey.")

        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input(
            "Password", type="password", key="login_password"
        )

        if st.button("Login to CineMatch", type="primary", use_container_width=True):
            success, user, message = login_user(login_username, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.is_guest = False
                st.success(message)
                st.rerun()
            else:
                st.error(message)
                st.info("💡 Having database trouble or want instant access? Use the **Fallback Node** below.")

        st.markdown(
            """
            <div style="margin: 22px 0 12px 0; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 14px;">
                <div style="font-size: 0.88rem; color: #d8b4fe; font-weight: 700; margin-bottom: 4px;">
                    ⚡ Quick Fallback Node
                </div>
                <div style="font-size: 0.82rem; color: #c4bdd8; margin-bottom: 12px;">
                    Bypass MongoDB authentication to explore recommendations instantly in guest mode.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚀 Enter via Fallback Node (Guest Mode)", key="quick_fallback_btn", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.username = "Guest"
            st.session_state.is_guest = True
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with register_tab:
        st.markdown('<div class="cm-panel">', unsafe_allow_html=True)
        st.subheader("Join CineMatch")
        st.caption("Create an account and start building your watchlist.")

        register_username = st.text_input(
            "Choose a username", key="register_username"
        )
        register_email = st.text_input(
            "Email address", key="register_email"
        )
        register_password = st.text_input(
            "Create a password", type="password", key="register_password"
        )
        confirm_password = st.text_input(
            "Confirm password", type="password", key="confirm_password"
        )

        if st.button("Create my account", type="primary", use_container_width=True):
            if register_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(
                    register_username, register_email, register_password
                )
                if success:
                    st.success(message)
                    st.info("Your account is ready. Switch to Login to sign in.")
                else:
                    st.error(message)
                    st.info("💡 You can also use the **Fallback Node** if database registration is unavailable.")
        st.markdown("</div>", unsafe_allow_html=True)

    with fallback_tab:
        st.markdown('<div class="cm-panel">', unsafe_allow_html=True)
        st.subheader("⚡ Fallback Node / Offline Demo")
        st.caption("High-availability mode designed for instant exploration and cloud deployments.")

        st.markdown(
            """
            <div style="padding: 16px; border-radius: 14px; background: rgba(139, 92, 246, 0.14); border: 1px solid rgba(168, 85, 247, 0.35); margin-bottom: 18px;">
                <div style="font-weight: 700; color: #f5d0fe; font-size: 1rem; margin-bottom: 8px;">
                    🎯 Why use the Fallback Node?
                </div>
                <ul style="color: #ddd6ed; font-size: 0.88rem; margin: 0; padding-left: 20px; line-height: 1.7;">
                    <li><strong>Zero Configuration:</strong> No database setup, passwords, or emails required.</li>
                    <li><strong>Cloud & Deployment Resilient:</strong> Works seamlessly on Streamlit Cloud even without MongoDB credentials.</li>
                    <li><strong>Full Machine Learning Features:</strong> Search all 4,800+ movies, calculate cosine similarity scores, and inspect metadata.</li>
                    <li><strong>Session Watchlist:</strong> Add and remove movies from your temporary session watchlist.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🌟 Launch with Fallback Node", type="primary", key="tab_fallback_btn", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.username = "Guest"
            st.session_state.is_guest = True
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="cm-footer">CINEMATCH · Find the film that fits your mood.</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ------------------------------------------
# SIDEBAR
# ------------------------------------------
st.sidebar.markdown(
    """
    <div style="padding: 10px 0 18px 0;">
        <div style="font-size:2rem;font-weight:800;font-family:Outfit,sans-serif;">
            🎬 Cine<span style="color:#e879f9;">Match</span>
        </div>
        <div style="color:#c4b5fd;font-size:0.78rem;letter-spacing:0.13em;">
            MOVIE DISCOVERY STUDIO
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.get("is_guest", False):
    st.sidebar.markdown("👋 Welcome, **Guest** ⚡ *(Fallback Mode)*")
    st.sidebar.caption("Temporary session mode. Database auth bypassed.")
else:
    st.sidebar.markdown(f"👋 Welcome, **{st.session_state.username}**")
    st.sidebar.caption("Your personal movie discovery space.")

page = st.sidebar.radio(
    "EXPLORE",
    ["Home", "Movie Recommendations", "My Watchlist", "About"],
    label_visibility="visible",
)

st.sidebar.markdown("---")
if st.sidebar.button("↪ Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_guest = False
    st.session_state.pop("recommendations", None)
    st.session_state.pop("recommendation_source", None)
    st.rerun()

st.sidebar.markdown(
    """
    <div style="margin-top:22px;padding:14px;border-radius:14px;
        background:rgba(139,92,246,0.12);border:1px solid rgba(196,181,253,0.16);">
        <div style="font-weight:700;color:#e9d5ff;">🍿 Movie night, sorted.</div>
        <div style="font-size:0.82rem;color:#c4bdd8;margin-top:5px;">
            Discover similar films and save the ones you want to watch.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------
# HOME PAGE
# ------------------------------------------
if page == "Home":
    st.markdown(
        """
        <div class="cm-hero">
            <div class="cm-brand">🎞️ YOUR PERSONAL MOVIE GUIDE</div>
            <h1>Find your next<br><span class="cm-gradient-text">favorite film.</span></h1>
            <p>One great movie leads to another. CineMatch uses content-based
            recommendations to help you discover films with similar themes,
            genres, keywords, actors, and directors.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎬 Movies in the library", f"{len(movies):,}")
    with col2:
        st.metric("🧠 Recommendation engine", "Content-based")
    with col3:
        st.metric("✨ Picks per search", "5 movies")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="cm-section-label">MADE FOR YOUR NEXT MOVIE NIGHT</div>', unsafe_allow_html=True)
    st.markdown("## Your movie discovery toolkit")

    feat1, feat2, feat3 = st.columns(3)
    with feat1:
        st.markdown(
            """<div class="cm-feature">
                <div class="cm-feature-icon">🔎</div>
                <div class="cm-feature-title">Discover similar films</div>
                <div class="cm-feature-copy">Choose a movie you love and explore titles with similar content.</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with feat2:
        st.markdown(
            """<div class="cm-feature">
                <div class="cm-feature-icon">💜</div>
                <div class="cm-feature-title">Build your watchlist</div>
                <div class="cm-feature-copy">Save interesting recommendations and keep your next watch in one place.</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with feat3:
        st.markdown(
            """<div class="cm-feature">
                <div class="cm-feature-icon">🎥</div>
                <div class="cm-feature-title">Follow the vibe</div>
                <div class="cm-feature-copy">Find your next adventure through movie metadata and similarity scores.</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🍿 Find movies for me", type="primary"):
        st.session_state.home_navigation_hint = True
        st.info("Choose **Movie Recommendations** from the sidebar to get started.")

# ------------------------------------------
# MOVIE RECOMMENDATIONS PAGE
# ------------------------------------------
elif page == "Movie Recommendations":
    st.markdown('<div class="cm-section-label">DISCOVER YOUR NEXT WATCH</div>', unsafe_allow_html=True)
    st.title("🍿 Find your next movie")
    st.write("Choose a film you enjoy, and CineMatch will find five similar movies.")

    movie_titles = sorted(movies["title"].dropna().unique().tolist())

    if not movie_titles:
        st.warning("No movie titles are available in the model.")
    else:
        selected_movie = st.selectbox("Choose a movie", movie_titles)

        if st.button("✨ Recommend movies", type="primary"):
            st.session_state.recommendations = recommend(selected_movie, 5)
            st.session_state.recommendation_source = selected_movie

        if (
            "recommendations" in st.session_state
            and st.session_state.get("recommendation_source") == selected_movie
        ):
            results = st.session_state.recommendations

            if results:
                st.markdown(f"## Similar to **{selected_movie}**")
                st.caption("Recommendations are ranked by their content similarity score.")

                for rank, movie in enumerate(results, start=1):
                    st.markdown('<div class="cm-movie-card">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([0.6, 1.5, 5])

                    with col1:
                        st.markdown(
                            f"<div style='padding-top:10px;font-family:Outfit,sans-serif;"
                            f"font-size:1.6rem;font-weight:800;color:#d8b4fe;'>"
                            f"#{rank:02d}</div>",
                            unsafe_allow_html=True,
                        )

                    with col2:
                        poster_path = movie.get("poster_path")
                        if (
                            isinstance(poster_path, str)
                            and poster_path.strip().startswith("/")
                        ):
                            poster_url = (
                                "https://image.tmdb.org/t/p/w500"
                                f"{poster_path.strip()}"
                            )
                            st.image(poster_url, width=145)
                        else:
                            st.markdown(
                                """
                                <div style="width:145px;height:218px;border-radius:13px;
                                    background:linear-gradient(145deg,#201333,#35152f);
                                    border:1px solid rgba(216,180,254,.2);
                                    display:flex;align-items:center;justify-content:center;
                                    text-align:center;color:#d8b4fe;padding:12px;">
                                    <div>🎬<br><br>Poster unavailable</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    with col3:
                        st.markdown(f"### {movie['title']}")
                        st.caption(
                            f"Content similarity score · {movie['similarity']:.3f}"
                        )
                        if st.button(
                            "💜 Add to Watchlist",
                            key=f"watchlist_{rank}_{movie['title']}",
                        ):
                            try:
                                success, message = add_to_watchlist(
                                    st.session_state.username, movie["title"]
                                )
                                if success:
                                    st.success(message)
                                else:
                                    st.warning(message)
                            except Exception as error:
                                st.error(f"Watchlist error: {error}")

                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.warning("No recommendations found.")

# ------------------------------------------
# MY WATCHLIST PAGE
# ------------------------------------------
elif page == "My Watchlist":
    st.markdown('<div class="cm-section-label">SAVED FOR LATER</div>', unsafe_allow_html=True)
    st.title("💜 My watchlist")
    st.write("All the films you've saved for your next movie night.")

    if st.session_state.get("is_guest", False):
        st.info("⚡ **Fallback Node Active:** Your watchlist is currently saved in temporary session memory.")

    watchlist = get_watchlist(st.session_state.username)

    if not watchlist:
        st.markdown(
            """
            <div class="cm-hero" style="text-align:center;padding:42px;">
                <div style="font-size:3rem;">🍿</div>
                <h2>Your next favorite is waiting.</h2>
                <p style="margin:0 auto;">Your watchlist is empty for now. Visit Movie Recommendations
                and save the films you want to watch.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"**{len(watchlist)}** movie(s) saved")
        for index, movie in enumerate(watchlist):
            movie_title = movie["movie_title"]
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"""<div class="cm-movie-card" style="padding:18px;margin-bottom:10px;">
                    <span style="color:#d8b4fe;font-weight:700;">🎬 &nbsp;{movie_title}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("Remove", key=f"remove_{movie_title}_{index}"):
                    success, message = remove_from_watchlist(
                        st.session_state.username, movie_title
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

# ------------------------------------------
# ABOUT PAGE
# ------------------------------------------
elif page == "About":
    st.markdown('<div class="cm-section-label">BEHIND THE RECOMMENDATIONS</div>', unsafe_allow_html=True)
    st.title("About CineMatch")
    st.markdown(
        """
        <div class="cm-hero" style="padding:30px;">
            <h2>Movies you'll love, <span class="cm-gradient-text">discovered differently.</span></h2>
            <p>CineMatch is a movie recommendation system built with Python and machine learning.
            It helps users discover films that share similar content characteristics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.markdown("### ✨ Key features")
        st.markdown(
            """
            - Content-based movie recommendations
            - Similarity scores for recommendations
            - User registration and login
            - Personal MongoDB-backed watchlist
            """
        )
    with right:
        st.markdown("### 🧠 Technology stack")
        st.markdown(
            """
            - **Python** — application logic
            - **Pandas / NumPy** — data processing
            - **Scikit-learn** — vectorization and similarity
            - **CountVectorizer** — movie metadata representation
            - **Cosine similarity** — ranking similar movies
            - **Streamlit** — web interface
            - **MongoDB** — accounts and watchlist storage
            """
        )

    st.info(
        "CineMatch uses content-based filtering. Its recommendations are based on "
        "movie metadata rather than personal ratings or collaborative user behavior."
    )

st.markdown(
    '<div class="cm-footer">🎬 CineMatch · Your personal movie discovery studio</div>',
    unsafe_allow_html=True,
)
