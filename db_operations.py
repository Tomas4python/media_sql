# Import libraries
import sqlite3
import logging
from typing import Optional


# Create a logger
logger = logging.getLogger(__name__)


def loggable(f):
    """A decorator that adds logging to a function."""
    def _inner(*args):
        logger.debug("Called function: '%s'", f.__name__)
        res = f(*args)
        if hasattr(res, '__len__'):
            logger.debug("Function '%s' returned %s results", f.__name__, len(res))
        else:
            logger.debug("Function '%s' returned a %s", f.__name__, type(res).__name__)
        return res
    return _inner


def initialize_database(db_name: str) -> None:
    """Create a database and its table if they do not exist."""

    conn = create_connection(db_name)
    if conn:
        if not check_table_exists(conn, "movies"):
            logger.info("Table 'movies' does not exist in '%s'. Creating new table.", str(db_name))
            create_table(conn)
        else:
            logger.info("Table 'movies' exists in '%s'.", str(db_name))
        conn.close()
    else:
        logger.warning("Failed to create a database connection for '%s'.", str(db_name))


def create_connection(db_file: str) -> Optional[sqlite3.Connection]:
    """Create a database connection to the SQLite database specified by db_file.
       If the database file does not exist, it will be created."""

    try:
        conn = sqlite3.connect(db_file)
        logger.info("Connected to SQLite database: '%s'.", str(db_file))
        return conn
    except sqlite3.Error:
        logger.exception("Error connecting to database: '%s'.", str(db_file))
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
    except sqlite3.Error:
        logger.exception("Error checking table existence.")
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
    except sqlite3.Error:
        logger.exception("Error checking table existence")


def movie_exists(conn: sqlite3.Connection, url: str) -> bool:
    """Check if a movie with the given url already exists in the database"""

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM movies WHERE url = ?", (url,))
        return cur.fetchone() is not None
    except sqlite3.Error:
        logger.exception(f"Error checking if movie exists.")
        return False


def insert_movie(conn: sqlite3.Connection, movie: tuple) -> None:
    """Insert a new movie into the movies table with URL"""

    sql = '''INSERT INTO movies(title, image, description, release_year, duration, genre, url, date_of_first_finding, 
    date_of_disappearance, related_persons, views_count, is_memorable) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, movie)
    conn.commit()


@loggable
def execute_query(query: str, databases: list[str]) -> list[tuple]:
    """Execute a query on both data and return the combined results."""
    results = []
    for database in databases:
        conn = create_connection(database)
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(query)
                results.extend(cur.fetchall())
                conn.close()
            except sqlite3.Error:
                logger.exception("Error executing query on database '%s'.", str(database))
                if conn:
                    conn.close()
    return results
