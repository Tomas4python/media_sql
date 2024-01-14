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
from config_loader import Config
import gui

# Create an instance of the Config class
config = Config().settings


def main():
    # Initialize both databases
    initialize_database(config["databases"]["database_epika"])
    initialize_database(config["databases"]["database_mediateka"])
    # Run graphical user interface
    gui.run_gui()


if __name__ == "__main__":
    main()
