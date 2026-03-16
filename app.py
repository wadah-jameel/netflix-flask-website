from flask import Flask, render_template

app = Flask(__name__)

# Static movie data — no API needed
MOVIES = [
    {
        "id": 1,
        "title": "Cosmic Odyssey",
        "genre": "Sci-Fi",
        "year": 2023,
        "rating": 8.9,
        "duration": "2h 28m",
        "description": "A team of astronauts embarks on a journey beyond the known universe, confronting the mysteries of space and time.",
        "banner_color": "#0a0a2e",
        "card_color": "#1a1a4e",
        "tags": ["Space", "Adventure", "Mind-bending"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/1/1c/Interstellar_film_poster.jpg"
    },
    {
        "id": 2,
        "title": "Shadow Protocol",
        "genre": "Action",
        "year": 2023,
        "rating": 7.8,
        "duration": "2h 05m",
        "description": "An elite spy uncovers a global conspiracy that threatens to rewrite the rules of international power.",
        "banner_color": "#1a0a0a",
        "card_color": "#3a1a1a",
        "tags": ["Spy", "Thriller", "Action"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/9/9b/Missionimpossible2.jpg"
    },
    {
        "id": 3,
        "title": "The Last Forest",
        "genre": "Drama",
        "year": 2022,
        "rating": 9.1,
        "duration": "1h 58m",
        "description": "A ranger's fight to protect the world's last ancient forest against powerful corporate interests.",
        "banner_color": "#0a1a0a",
        "card_color": "#1a3a1a",
        "tags": ["Nature", "Drama", "Inspiring"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/b/b1/A_Beautiful_Mind_Poster.jpg"
    },
    {
        "id": 4,
        "title": "Neon Samurai",
        "genre": "Action",
        "year": 2023,
        "rating": 8.2,
        "duration": "2h 15m",
        "description": "In a cyberpunk Tokyo, a disgraced samurai fights his way through neon-lit streets to reclaim his honor.",
        "banner_color": "#1a001a",
        "card_color": "#2a002a",
        "tags": ["Cyberpunk", "Action", "Japan"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/2/2c/The_matrix_poster.jpg"
    },
    {
        "id": 5,
        "title": "Frozen Depths",
        "genre": "Thriller",
        "year": 2022,
        "rating": 7.5,
        "duration": "1h 52m",
        "description": "A marine biologist discovers an ancient creature beneath Arctic ice, triggering a deadly chain of events.",
        "banner_color": "#001a2a",
        "card_color": "#002a3a",
        "tags": ["Creature", "Arctic", "Survival"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/8/8a/The_Thing_%281982_film%29_poster.jpg"
    },
    {
        "id": 6,
        "title": "City of Ghosts",
        "genre": "Horror",
        "year": 2023,
        "rating": 7.9,
        "duration": "1h 45m",
        "description": "A paranormal investigator unravels the dark history of a city haunted by its own buried secrets.",
        "banner_color": "#0d0d0d",
        "card_color": "#1a1a1a",
        "tags": ["Horror", "Mystery", "Paranormal"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/1/1f/The_Shining_%281980_film%29_poster.jpg"
    },
    {
        "id": 7,
        "title": "Velocity",
        "genre": "Action",
        "year": 2022,
        "rating": 7.2,
        "duration": "1h 55m",
        "description": "The world's fastest street racer must outrun a criminal syndicate across three continents.",
        "banner_color": "#1a1000",
        "card_color": "#2a1800",
        "tags": ["Racing", "Cars", "Heist"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/b/bd/Mad_Max_Fury_Road.jpg"
    },
    {
        "id": 8,
        "title": "Parallel Lives",
        "genre": "Sci-Fi",
        "year": 2023,
        "rating": 8.6,
        "duration": "2h 10m",
        "description": "A physicist accidentally opens a portal to parallel universes, meeting alternate versions of everyone she loves.",
        "banner_color": "#0a0a1a",
        "card_color": "#15153a",
        "tags": ["Multiverse", "Drama", "Sci-Fi"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/3/3b/Inception_Movie_Poster.jpg"
    },
    {
        "id": 9,
        "title": "Heartlands",
        "genre": "Drama",
        "year": 2022,
        "rating": 8.4,
        "duration": "2h 02m",
        "description": "Three generations of a farming family navigate love, loss, and change across fifty years of American history.",
        "banner_color": "#1a0f00",
        "card_color": "#2a1800",
        "tags": ["Family", "History", "Emotional"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/a/a2/Forrest_Gump_poster.jpg"
    },
    {
        "id": 10,
        "title": "The Algorithm",
        "genre": "Thriller",
        "year": 2023,
        "rating": 8.0,
        "duration": "1h 48m",
        "description": "A whistleblower exposes a tech giant's AI that has quietly been manipulating world events for a decade.",
        "banner_color": "#001a1a",
        "card_color": "#003030",
        "tags": ["Tech", "AI", "Conspiracy"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/f/f6/Enemy_of_the_State_poster.jpg"
    },
    {
        "id": 11,
        "title": "Ember",
        "genre": "Drama",
        "year": 2022,
        "rating": 8.7,
        "duration": "1h 56m",
        "description": "A firefighter haunted by a past tragedy finds redemption while battling the most destructive wildfire in history.",
        "banner_color": "#1a0500",
        "card_color": "#2a0800",
        "tags": ["Firefighter", "Redemption", "Drama"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/8/8f/Ladder_49_film.jpg"
    },
    {
        "id": 12,
        "title": "Deep Signal",
        "genre": "Sci-Fi",
        "year": 2022,
        "rating": 7.7,
        "duration": "2h 00m",
        "description": "Earth receives a signal from deep space. What follows changes humanity's understanding of its place in the cosmos.",
        "banner_color": "#00001a",
        "card_color": "#00002a",
        "tags": ["Aliens", "First Contact", "Sci-Fi"],
        "poster": "https://upload.wikimedia.org/wikipedia/en/6/6c/Arrival_%28film%29_poster.jpg"
    },
]

# Group movies by genre
def get_movies_by_genre():
    genres = {}
    for movie in MOVIES:
        genre = movie["genre"]
        if genre not in genres:
            genres[genre] = []
        genres[genre].append(movie)
    return genres


@app.route("/")
def index():
    hero = MOVIES[0]
    genres = get_movies_by_genre()
    return render_template("index.html", hero=hero, genres=genres)


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = next((m for m in MOVIES if m["id"] == movie_id), None)
    if not movie:
        return render_template("404.html"), 404
    # Get similar movies (same genre, excluding current)
    similar = [m for m in MOVIES if m["genre"] == movie["genre"] and m["id"] != movie_id][:4]
    return render_template("movie.html", movie=movie, similar=similar)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
