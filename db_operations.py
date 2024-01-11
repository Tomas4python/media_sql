# Import libraries
import sqlite3
from typing import Optional


def initialize_database(db_name: str) -> None:
    """Create a database and its table if they do not exist."""
    conn = create_connection(db_name)
    if conn:
        if not check_table_exists(conn, "movies"):
            print(f"Table 'movies' does not exist in '{db_name}'. Creating new table.")
            create_table(conn)
        else:
            print(f"Table 'movies' exists in '{db_name}'.")
        conn.close()
    else:
        print(f"Failed to create a database connection for '{db_name}'.")


def create_connection(db_file: str) -> Optional[sqlite3.Connection]:
    """Create a database connection to the SQLite database specified by db_file.
       If the database file does not exist, it will be created."""

    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database: {db_file}.")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}.")
        return None


def check_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if a specific table exists in the database"""

    try:
        cur = conn.cursor()
        cur.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cur.fetchone()[0] == 1:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"Error checking table existence: {e}.")
        return False


def create_table(conn: sqlite3.Connection) -> None:
    """Create a table for storing movie data"""

    sql_create_movies_table = """ CREATE TABLE IF NOT EXISTS movies (
                                        id INTEGER PRIMARY KEY,
                                        title TEXT NOT NULL,
                                        image BLOB,
                                        description TEXT,
                                        release_year INTEGER,
                                        duration INTEGER,
                                        genre TEXT,
                                        url TEXT,
                                        date_of_first_finding TEXT,
                                        date_of_disappearance TEXT,
                                        related_persons TEXT,
                                        views_count INTEGER,
                                        is_memorable BOOLEAN
                                    ); """
    try:
        c = conn.cursor()
        c.execute(sql_create_movies_table)
    except sqlite3.Error as e:
        print(e)


def movie_exists(conn: sqlite3.Connection, url: str) -> bool:
    """Check if a movie with the given url already exists in the database"""

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM movies WHERE url = ?", (url,))
        return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"Error checking if movie exists: {e}.")
        return False


def insert_movie(conn: sqlite3.Connection, movie: tuple) -> None:
    """Insert a new movie into the movies table with URL"""

    sql = ''' INSERT INTO movies(title, image, description, release_year, duration, genre, url,
                                 date_of_first_finding, date_of_disappearance, related_persons, views_count, is_memorable)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, movie)
    conn.commit()


def execute_query(query: str, databases: list[str]) -> list[tuple]:
    """Execute a query on both databases and return the combined results."""
    results = []
    for database in databases:
        conn = create_connection(database)
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(query)
                results.extend(cur.fetchall())
                conn.close()
            except sqlite3.Error as e:
                print(f"Error executing query on database '{database}': {e}.")
                if conn:
                    conn.close()
    return results

#
# def remove_duplicate_movies(conn: sqlite3.Connection) -> None:
#     """Remove duplicate movies from the database, keeping only the first insertion."""
#
#     try:
#         cur = conn.cursor()
#
#         # Find duplicate URLs
#         cur.execute("SELECT url FROM movies GROUP BY url HAVING COUNT(url) > 1")
#         duplicates = cur.fetchall()
#
#         for url in duplicates:
#             # For each duplicate URL, find all movie IDs
#             cur.execute("SELECT id FROM movies WHERE url = ?", (url[0],))
#             ids = [id_tuple[0] for id_tuple in cur.fetchall()]
#
#             # Keep the first movie (based on some criteria, e.g., the earliest date_of_first_finding)
#             # and delete the rest
#             ids_to_delete = ids[1:]  # Adjust as needed based on which one you want to keep
#             cur.executemany("DELETE FROM movies WHERE id = ?", [(id,) for id in ids_to_delete])
#
#         conn.commit()
#         print(f"Removed duplicates for {len(duplicates)} URLs.")
#
#     except sqlite3.Error as e:
#         print(f"Error removing duplicates: {e}.")
#         conn.rollback()
