import yaml

config_dict = dict()

# Set up GUI options
config_dict["gui"] = {
    "app_name": "CAAI Project 1 - scraping/SQLite3 app",
    "gui_window_size": "1900x800",
}

# Set up databases
config_dict["databases"] = {
    "database_epika": "epika_movies.db",
    "database_mediateka": "mediateka_movies.db",
    "database_epika_demo": "epika_movies_demo.db",
    "database_mediateka_demo": "mediateka_demo.db",
}

# Set up Chrome driver options (--headless if False) and scraping options
config_dict["scraping"] = {
    "show_browser": False,
    "lazy_scroll_step": 500,
    "wait_time": 0.5,
}

with open("config.yaml","w", encoding="utf-8") as file_object:
    yaml.dump(config_dict,file_object)