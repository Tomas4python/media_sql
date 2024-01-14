# Import libraries
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
import requests
from typing import Optional
import time
import re

# Import functions and classes from other modules of the app
from config_loader import Config


# Create a logger
logger = logging.getLogger(__name__)

# Create an instance of the Config class
config = Config().settings

class WebDriverContext:
    """Context manager for scraping functions to load, start and quit Chrome driver"""

    def __enter__(self) -> webdriver.Chrome:
        # Set up Chrome options
        chrome_options = Options()
        LOGGER.setLevel(logging.CRITICAL)  # Limit selenium logs
        chrome_options.add_argument("--log-level=3")  # Set log level to minimize messages
        if config["scraping"]["show_browser"] is False:
            chrome_options.add_argument("--headless")  # Run in headless mode

        # Set up WebDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.driver.quit()


def accept_cookies(driver):
    """Clicks cookie acceptance dialog button for epika.lrt.lt"""

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Sutikti ir judėti toliau']"))
        ).click()

    except Exception as e:
        logger.warning("Cookie consent handling error: %s", e)


def load_lazy_content(driver, scroll_step=config["scraping"]["lazy_scroll_step"], wait_time=config["scraping"]["wait_time"]):
    """Scroll epika.lrt.lt page to load lazy content"""

    # Get the current scroll position
    current_position = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop")
    logger.info("Current position: %s", current_position)

    # Find max height of the page
    max_height = driver.execute_script("return document.body.scrollHeight")
    logger.info("Max height: %s", max_height)

    # Step by step scroll page while content downloads
    logger.info("Scrolling...")
    for scroll_position in range(current_position, max_height, scroll_step):
        print(f"Scroll position: {scroll_position}", end='\r')
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(wait_time)
    print("\n")

    # Final scroll to the bottom to ensure all content is loaded
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(wait_time)


def read_image_from_url(url: str) -> Optional[bytes]:
    """Download an image from a URL and return it as a binary blob"""

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logger.warning("Error while fetching the image: %s", e)
        return None


def shallow_scrape_epika(driver: webdriver.Chrome) -> list[tuple[str, str, str]]:
    """Scrape epika.lrt.lt page for media information based on the list of search strings."""

    logging.info("Starting shallow scraping...")
    # Open web page for the first time and accept the cookies
    driver.get("https://epika.lrt.lt/search")
    accept_cookies(driver)
    logging.info("Cookies accepted")

    # Initialize the list of movies for return as function result
    list_of_movies: list[tuple[str, str, str]] = []

    # Loop through all search strings
    for ind, search_string in enumerate(config["scraping"]["list_search_strings_epika"]["short"], start=1):
        logging.info("Shallow scraping - page %s of %s", ind, len(config["scraping"]["list_search_strings_epika"]["short"]))
        counter_str_used = 0  # To count additions in relation to search string
        try:
            # Open the webpage
            driver.get(f"https://epika.lrt.lt/search?q={search_string}")

            time.sleep(2)  # Allow to load whole body of the page

            # Easy scroll the page to the bottom to download its content
            load_lazy_content(driver)

            # Find all media blocks
            title_blocks = driver.find_elements(By.CSS_SELECTOR, ".tile--vod.tile")
            logging.info("Found %s movie title. Extracting...", len(title_blocks))

            for i, block in enumerate(title_blocks):
                try:
                    # Extract title, link to page, and link to image
                    movie_title = block.find_element(By.CSS_SELECTOR, ".headline-4.tile__title").text
                    link_to_page = block.find_element(By.CLASS_NAME, "tile__link").get_attribute("href")
                    link_to_image = block.find_element(By.CLASS_NAME, "cover").get_attribute("src")
                    print("." * i, end='\r')

                    # No way further with this movie, if one element is missing
                    assert movie_title is not None, "Movie title is None"
                    assert link_to_page is not None, "Link to page is None"
                    assert link_to_image is not None, "Link to image is None"
                    # Check if the movie title is already in the list
                    if not any(link_to_page == existing_url for _, existing_url, _ in list_of_movies):
                        # Add the tuple to the list
                        counter_str_used += 1
                        list_of_movies.append((movie_title, link_to_page, link_to_image))

                except NoSuchElementException as err:
                    logging.warning("Element not found: %s", err)

        except Exception as e:
            logging.exception(f"An error occurred while processing '{search_string}'.", search_string)

        print(f'\nString: "{search_string}" | Returns: {len(title_blocks)} | Used: {counter_str_used}')
        time.sleep(2)  # Make pause between scraping next page

    logging.info("Shallow scraping finished.")
    return list_of_movies


def deep_scrape_epika(driver: webdriver.Chrome, list_of_movies: list[tuple[str, str, str]]) -> list[
    tuple[str, bytes, str, int, int, str, str]]:
    """Scrape epika.lrt.lt particular movie page for additional information of the movie."""

    logging.info("Starting deep scraping...")
    # Open web page for the first time and accept the cookies
    driver.get("https://epika.lrt.lt/search")
    time.sleep(2)
    accept_cookies(driver)
    logging.info("Cookies accepted")

    # Initialize the list of movie data for return as function result
    # Tuple structure: <title, image, description, release year, duration, genre, page url>
    list_of_movie_data: list[tuple[str, Optional[bytes], str, int, int, str, str]] = []

    for ind, movie in enumerate(list_of_movies, start=1):
        print(f"Scraping {ind} of {len(list_of_movies)}", end='\r')
        try:
            driver.get(f"{movie[1]}")
            time.sleep(1)  # Allow the page to load

            # Initialize variables
            release_year = None
            genre = []
            total_minutes = None

            try:
                metadata_container = driver.find_element(By.CSS_SELECTOR, 'div.metadata__product-meta')
                metadata_elements = metadata_container.find_elements(By.CSS_SELECTOR,
                                                                     'span.metadata__product-meta-element')

                for element in metadata_elements:
                    text = element.text.strip()

                    if text.isdigit() and len(text) == 4:
                        release_year = int(text)
                    elif re.match(r'(?:(\d+)h\s*)?(\d+)m', text):
                        match = re.match(r'(?:(\d+)h\s*)?(\d+)m', text)
                        hours, minutes = map(lambda x: int(x) if x else 0, match.groups())
                        total_minutes = hours * 60 + minutes
                    else:
                        genre.append(text)

                genre = ', '.join(genre)

            except Exception as e:
                logging.warning("Error extracting metadata: %s", e)

            try:
                description = driver.find_element(By.CSS_SELECTOR, 'div.metadata-content__description').text.strip()
            except NoSuchElementException as err:
                logging.warning("Description not found: %s", err)
                description = ""

            image = read_image_from_url(movie[2])

            # Append the movie data to the list
            list_of_movie_data.append((movie[0], image, description, release_year, total_minutes, genre, movie[1]))

            # Assertions
            assert release_year is not None, "Release year is None"
            assert genre != "", "Genre is None"
            assert total_minutes is not None, "Duration is None"
            assert description != "", "Description is None"
            assert image is not None, "Image is None"

        except Exception as e:
            logging.info("Element not found '%s': %s", movie[0], e)

        time.sleep(1)  # Pause between scraping pages

    logging.info("Deep scraping finished.")
    return list_of_movie_data


def decline_cookies(driver):
    """Clicks cookie acceptance dialog button for lrt.lt/tema/filmai"""

    try:
        wait = WebDriverWait(driver, 10)  # Increased timeout
        wait.until(EC.presence_of_element_located((By.ID, "CybotCookiebotDialogBodyButtonDecline")))
        wait.until(EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))).click()
        logging.info("Clicked cookie decline button.")
    except Exception as e:
        logging.warning("Cookie consent handling error: %s", e)


def click_optional_buttons(driver: webdriver.Chrome):
    """Clicks on lrt.lt/tema/filmai page optional buttons if they appear."""

    buttons_to_check = [
        ("//button[.//span[text()='Man jau yra 7 metai']]", "Clicked 7 years age acceptance button.", "7 years age acceptance button not found."),
        ("//button[.//span[text()='Man jau yra 14 metų']]", "Clicked 14 years age acceptance button.", "14 years age acceptance button not found."),
        ("//button[.//span[text()='Man jau yra 18 metų']]", "Clicked 18 years age acceptance button.", "18 years age acceptance button not found."),
        ("//a[text()='Daugiau']", "Clicked 'Load more' button.", "'Load more' button not found.")
    ]

    for xpath, success_message, fail_message in buttons_to_check:
        try:
            if driver.find_elements(By.XPATH, xpath):
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                ).click()
                logging.info(success_message)
        except (NoSuchElementException, ElementNotInteractableException, TimeoutException):
            logging.info(fail_message)


def convert_duration_to_minutes(duration_str: str) -> int:
    """Converts duration strings from lrt.lt/tema/filmai page to minutes"""

    parts = duration_str.split(":")
    try:
        if len(parts) == 3:
            # Format is HH:MM:SS
            hours, minutes, _ = map(int, parts)
            return hours * 60 + minutes
        elif len(parts) == 2:
            # Format is MM:SS
            minutes, _ = map(int, parts)
            return minutes
    except ValueError:
        return None
    return None


def shallow_scrape_mediateka(driver: webdriver.Chrome) -> list[tuple[str, str, str, str, str]]:
    """Scrape lrt.lt/tema/filmai page for media information."""

    logging.info("Starting shallow scraping...")

    try:
        # Open the webpage
        driver.get("https://www.lrt.lt/tema/filmai")
        time.sleep(2) # Allow cookie consent to appear
        decline_cookies(driver)
        logging.info("Starting downloading web content...")

        i = 0
        while True:
            try:
                # Easy scroll the page to the bottom to download its content
                load_lazy_content(driver)
                # Find and click the "Load More" button
                load_more_button = driver.find_element(By.XPATH, '//a[@class="btn btn--lg section__button"]')
                load_more_button.click()
                i += 1
                # Debugging
                if i == 2:
                    break
                logging.info(f"Load more button clicked {i} times")
                time.sleep(2)  # Wait for the page to load more content

            except (NoSuchElementException, ElementNotInteractableException):
                logging.info("No more 'Load more' buttons.")
                break

        # Find all media blocks
        news_blocks = driver.find_elements(By.CLASS_NAME, "news")
        logging.info("Blocks loaded: %s", len(news_blocks))

        # Initialize a list to store the tuples for return as function result
        media_info = []

        # Loop through each news block
        for ind, block in enumerate(news_blocks):
            print(f"Processing block: {ind + 1}", end='\r')

            # Check if the specific icon element exists, skip if it does - not movie
            if block.find_elements(By.CSS_SELECTOR, "svg.svg-icon.badge-light") or block.find_elements(By.CSS_SELECTOR,
                                                                                                       "i.icon.icon"
                                                                                                       "-photo"):
                continue

            # Extract the title and link
            title_element = block.find_element(By.CSS_SELECTOR, "h3.news__title a")
            title = title_element.text
            link = title_element.get_attribute("href")

            # Extract image link
            image_link = block.find_element(By.CSS_SELECTOR, ".media-block__image").get_attribute(
                "src")

            # Extract the duration
            duration = block.find_element(By.CLASS_NAME, "media-block__duration").text if block.find_elements(
                By.CLASS_NAME, "media-block__duration") else "None"

            # Extract the count of views
            views = block.find_element(By.CSS_SELECTOR,
                                       ".badge-list.media-block__badge-list .badge.badge-light > span:last-child").text if block.find_elements(
                By.CSS_SELECTOR, ".badge-list.media-block__badge-list .badge.badge-light > span:last-child") else "None"

            # Check if both duration and views do not exist, skip - not a movie
            if duration == 'None' and views == 'None':
                continue

            # Add the tuple to the list
            media_info.append((title, link, image_link, duration, views))

        print("\n")
        logging.info("Shallow scraping finished.")
        return media_info

    except Exception as e:
        logging.exception("An error occurred during scraping")
        return []


def deep_scrape_mediateka(
        driver: webdriver.Chrome, list_of_movies: list[tuple[str, str, str, str, str]]
) -> list[tuple[str, Optional[bytes], str, int, int, str, str, int]]:
    """Scrape lrt.lt/tema/filmai particular movie page for movie information."""

    logging.info("Starting deep scraping...")

    # JavaScript to pause the video
    pause_video_script = """
    var videoElements = document.querySelectorAll('video');
    for (var i = 0; i < videoElements.length; i++) {
        videoElements[i].pause();
    }
    """

    # Open web page for the first time and accept the cookies
    driver.get("https://www.lrt.lt/tema/filmai")
    time.sleep(3)  # Allow cookie consent to download
    decline_cookies(driver)

    # Initialize the list of movie data for return as function result
    # Tuple structure: <title, image, description, release year, duration, genre, page url, views>
    list_of_movie_data: list[tuple[str, Optional[bytes], str, int, int, str, str, int]] = []

    for ind, movie in enumerate(list_of_movies, start=1):
        logging.info("Scraping %s of %s", ind, len(list_of_movies))
        try:
            driver.get(f"{movie[1]}")
            time.sleep(2)  # Allow the page to load
            driver.execute_script(pause_video_script)
            click_optional_buttons(driver)

            # Initialize variables
            description = genre = image = duration = views = None

            try:
                # Extract description
                paragraph_elements = driver.find_elements(By.CSS_SELECTOR,
                                                          ".article-content.article-content--sm.mt-16.js-text"
                                                          "-selection p")
                description = ' '.join([element.text for element in paragraph_elements])

                # Look in the description if there genre is mentioned
                all_text_lower = description.lower()
                for genre_candidate in config["scraping"]["list_of_genres_mediateka"]:
                    if genre_candidate in all_text_lower:
                        genre = genre_candidate
                        break

                # Search for release year in the format '2018 m.'
                year_match = re.search(r'\b(\d{4})\s*m\.', all_text_lower)
                release_year = int(year_match.group(1)) if year_match else None

                image = read_image_from_url(movie[2])
                duration = convert_duration_to_minutes(movie[3])
                views = int(movie[4]) if movie[4].isdigit() else None

                print(f"Title: {movie[0]} | Description: {description[:20]} | Release year: {release_year} | Genre: {genre} | Duration: {duration} | Views: {views}\n")
                # Append the movie data to the list
                list_of_movie_data.append(
                    (movie[0], image, description, release_year, duration, genre, movie[1], views))

                assert description is not None, "Description is None"
                assert release_year is not None, "Release year is None"
                assert genre is not None, "Genre is None"
                assert image is not None, "Image is None"
                assert duration is not None, "Duration is None"
                assert views is not None, "Views is None"

            except Exception as e:
                logging.info("Element not found extracting description: %s", e)

        except Exception as e:
            logging.exception("An error occurred while processing '%s'", movie[0])

        time.sleep(1)  # Pause between scraping pages

    logging.info("Deep scraping finished.")
    return list_of_movie_data
