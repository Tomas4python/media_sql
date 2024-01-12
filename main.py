# Scraping app of two media sites https://epika.lrt.lt and https://www.lrt.lt/tema/filmai
# The app is coded with only purpose of learning python coding, in particular Selenium and SQLite3
# The app is coded with Python 3.11

# Import libraries
import logging.config

# Configure logging
logging.config.fileConfig('logging.ini')

# Initialise logger
logger = logging.getLogger(__name__)
logger.info("Initialize logger")

# Import functions and classes from other modules of the app
from db_operations import initialize_database
from config import Config
import gui


def main():
    # Initialize both databases
    initialize_database(Config.database_epika)
    initialize_database(Config.database_mediateka)
    # Run graphical user interface
    gui.run_gui()


if __name__ == "__main__":
    main()
