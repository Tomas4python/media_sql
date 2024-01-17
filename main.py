# Scraping app of two media sites https://epika.lrt.lt and https://www.lrt.lt/tema/filmai
# The app is coded with only purpose of learning python coding, in particular Selenium and SQLite3
# The app is coded with Python 3.11

# Import libraries
import argparse
import logging.config

# Configure logging
logging.config.fileConfig('logging.ini')  # Load config file before import of other modules

# Import functions and classes from other modules of the app
from db_operations import initialize_database
from config_loader import Config
import gui

# Initialise logger
logger = logging.getLogger(__name__)
logger.info("Initialize logger")

# Create an instance of the Config class and modify settings based on args
config = Config().settings


def parse_arguments() -> argparse.Namespace:
    """Parse arguments provided from command line"""
    parser = argparse.ArgumentParser(description=config['gui']['app_description'])
    parser.add_argument('mode', choices=['demo'], nargs='?', default=None, help='Run the program in demo mode')
    parser.add_argument('demo_search_strings_epika', nargs='?', type=eval, default=config["demo"]["default_demo_search_strings_epika"],
                        help='Optional list of search strings for Epika')
    parser.add_argument('-b', '--show_browser', action='store_true', help='Show scraping action in browser if set')
    return parser.parse_args()

def main():
    args = parse_arguments()

    if args.mode == 'demo':
        config['demo']['is_demo'] = True
        config['data']['epika'] = config['data']['epika_demo']
        config['data']['mediateka'] = config['data']['mediateka_demo']
        config['demo']['default_demo_search_strings_epika'] = args.demo_search_strings_epika

    if args.show_browser:
        config['scraping']['show_browser'] = True

    # Initialize both data
    initialize_database(config["data"]["epika"])
    initialize_database(config["data"]["mediateka"])

    # Run graphical user interface
    gui.run_gui()

if __name__ == "__main__":
    main()
