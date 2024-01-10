# Import libraries
import os
import csv
from datetime import datetime
import sqlite3

# Import functions and classes from other modules of the app
from db_operations import create_connection, movie_exists, insert_movie
from scraping import shallow_scrape_epika, deep_scrape_epika, shallow_scrape_mediateka, \
    deep_scrape_mediateka


def shallow_scrape_wrapper(driver, database, filename):
    """Checks if previous file exist, as well for the same movies in database and writes additional scrape
    results to csv file"""

    # Check if previous shallow scrape exists, if new shallow scrape needed, delete csv file manually
    if os.path.exists(filename):
        print(f"File '{filename}' already exists. Skipping shallow scrape.")
        return

    # Perform shallow scrape
    if filename == 'shallow_scrape_result_epika.csv':
        results = shallow_scrape_epika(driver)
    else:
        results = shallow_scrape_mediateka(driver)
    print(f"\nShallow scrape results returned: {len(results)}")

    # Filter out movies that already exist in the database by movie url (sometimes the titles are the same)
    conn = create_connection(database)
    results_filtered = [movie for movie in results if not movie_exists(conn, movie[1])]
    conn.close()
    print(f"\nThe list of {len(results_filtered)} new movies prepared to add to database '{database}'")

    # Write filtered results to CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(results_filtered)
        print(f"Shallow scraping data temporarily written to file '{filename}'")


def deep_scrape_wrapper(driver, database, shallow_filename):
    """Checks if shallow scrape file exist and writes deep scrape results to sqlite3 database"""

    # Check if shallow scrape was successfully created
    if not os.path.exists(shallow_filename):
        print(f"File '{shallow_filename}' does not exist. Cannot perform deep scrape.")
        return

    # Read data from the shallow scrape CSV file
    with open(shallow_filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        data_list = [tuple(row) for row in reader]

    # Perform deep scrape
    if shallow_filename == 'shallow_scrape_result_epika.csv':
        results = deep_scrape_epika(driver, data_list)
    else:
        results = deep_scrape_mediateka(driver, data_list)
    print(f"\nDeep scrape results returned: {len(results)}")

    # Write results to database
    conn = create_connection(database)
    counter = 0
    try:
        # Start a transaction
        conn.execute('BEGIN')
        # Insert each movie into the database
        for movie in results:
            counter += 1
            # Add the current timestamp to date_of_first_finding
            if shallow_filename == 'shallow_scrape_result_epika.csv':
                movie_with_timestamp = movie + (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, None, None, False)
                insert_movie(conn, movie_with_timestamp)
            else:
                movie_with_timestamp = (movie[0], movie[1], movie[2], movie[3], movie[4], movie[5], movie[6],
                                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, None, movie[7], False)
                insert_movie(conn, movie_with_timestamp)
        # Commit the transaction
        conn.commit()
        print(f"\n{counter} new movies added to database '{database}'")
    except sqlite3.Error as e:
        # Roll back any change if error occurs
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()

    # Remove the shallow scrape file
    os.remove(shallow_filename)


# def remove_duplicates_from_database(database):
#     """Removes duplicate movies from database"""

#     conn = create_connection(database)
#     if conn:
#         remove_duplicate_movies(conn)
#         conn.close()
