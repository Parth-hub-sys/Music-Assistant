import json
from sqlalchemy import text
from langchain_core.tools import tool
from retrieval.db_engine import engine

def safe_tool_result(result):
    """Ensures tool result is a non-empty JSON string for Groq compatibility."""
    res_str = json.dumps(result, default=str)
    return res_str if res_str and res_str != "[]" else "[]"

@tool
def get_albums_by_artist(artists: list[str]) -> str:
    """Retrieves all albums for one or more artist names. Always pass ALL requested artists as a list, e.g. ['AC/DC', 'Aerosmith']."""
    results = []
    with engine.connect() as connection:
        for artist in artists:
            query = text("""
                SELECT album.title, artist.name
                FROM album
                JOIN artist ON album.artist_id = artist.artist_id
                WHERE artist.name ILIKE :artist
                LIMIT 100
            """)
            rows = connection.execute(query, {"artist": artist}).fetchall()
            if rows:
                results.extend([{"Artist": row[1], "Album": row[0]} for row in rows])
            else:
                results.append({"Artist": artist, "Album": "No albums found in database"})
    return safe_tool_result(results)

@tool
def get_tracks_by_artist(artist: str) -> str:
    """Retrieves all tracks for a given artist."""
    query = text("SELECT track.name FROM track JOIN album ON track.album_id = album.album_id JOIN artist ON album.artist_id = artist.artist_id WHERE artist.name = :artist LIMIT 100")
    with engine.connect() as connection:
        result = connection.execute(query, {"artist": artist})
        return safe_tool_result([row[0] for row in result.fetchall()])

@tool
def get_songs_by_genre(genre: str) -> str:
    """Retrieves all songs for a given genre (case-insensitive, partial match)."""
    query = text("""
        SELECT track.name, artist.name AS artist
        FROM track
        JOIN genre ON track.genre_id = genre.genre_id
        JOIN album ON track.album_id = album.album_id
        JOIN artist ON album.artist_id = artist.artist_id
        WHERE genre.name ILIKE :genre
        LIMIT 100
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"genre": f"%{genre}%"})
        rows = result.fetchall()
        if not rows:
            return f"No songs found in the database for genre: '{genre}'. Do not guess or generate song names."
        return safe_tool_result([{"Track": row[0], "Artist": row[1]} for row in rows])

@tool
def check_for_songs(song_name: str) -> str:
    """Checks if a song exists in the catalog."""
    query = text("SELECT name FROM track WHERE name = :song_name")
    with engine.connect() as connection:
        result = connection.execute(query, {"song_name": song_name})
        found = result.fetchone() is not None
        return "Song found" if found else "Song not found"

@tool
def get_genre_by_song(song_name: str) -> str:
    """Retrieves the genre of a specific song by its name (case-insensitive)."""
    query = text("""
        SELECT track.name, genre.name AS genre
        FROM track
        JOIN genre ON track.genre_id = genre.genre_id
        WHERE track.name ILIKE :song_name
        LIMIT 1
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"song_name": song_name})
        row = result.fetchone()
        if row:
            return safe_tool_result({"Track": row[0], "Genre": row[1]})
        return "Song not found"

music_tools = [get_albums_by_artist, get_tracks_by_artist, get_songs_by_genre, check_for_songs, get_genre_by_song]
