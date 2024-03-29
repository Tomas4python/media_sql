import yaml


class Config:
    """This class loads configuration from config.yaml"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            with open("config.yaml", "r", encoding="utf-8") as file:
                cls._instance.data = yaml.safe_load(file)
        return cls._instance

    @property
    def settings(self):
        return self._instance.data


class LargeStrings:
    """Class to keep large lists of strings used for scraping and GUI configuration"""

    # Set how many epika.lrt.lt search pages results to scrape by stetting search strings in list
    list_search_strings_epika: list[str] = [
            "ant", "ing", "tai", "kur", "dži",  # Lithuanian_trigrams
            "sta", "gal", "sav", "pav", "tar",
            "tik", "lab", "vis", "ger", "tie",
            "nie", "art", "met", "kas", "tuo",
            "jau", "būt", "vak", "dar", "man",
            "sen", "aps", "tik", "ėjo", "nes",
            "vie", "lia", "jim", "ten", "jos",
            "šio", "dėl", "kit", "dar", "kai",
            "pas", "sak", "prie", "min", "tur",
            "kie", "buv", "mat", "toj", "ką*",
            "tam", "žmo", "pri", "pat", "dir",

            "pa*", "pr*", "ne*", "ka*", "te*",  # Lithuanian_bigrams
            "na*", "jo*", "ap*", "da*", "ja*",
            "is*", "ta*", "ma*", "ti*", "ju*",
            "no*", "ko*", "su*", "sa*", "ki*",
            "me*", "ga*", "to*", "la*", "gr*",
            "po*", "ge*", "di*", "at*", "ba*",
            "nu*", "se*", "vi*", "ku*", "mi*",
            "tr*", "pi*", "st*", "va*", "ie*",
            "ma*", "ri*", "le*", "ra*", "ar*",
            "am*", "tu*", "re*", "bu*", "as*",
            "de*", "an*", "ir*", "al*", "mo*",

            "a**", "ą**", "b**", "c**", "č**",  # Lithuanian_letters_and_numbers
            "d**", "e**", "ę**", "ė**", "f**",
            "g**", "h**", "i**", "į**", "y**",
            "j**", "k**", "l**", "m**", "n**",
            "o**", "p**", "r**", "s**", "š**",
            "t**", "u**", "ų**", "ū**", "v**",
            "z**", "ž**", "0**", "1**", "2**",
            "3**", "4**", "5**", "6**", "7**",
            "8**", "9**",

            "the", "and", "ing", "her", "ere", "ent", "tha", "nth", "was", "eth",  # English_trigrams
            "for", "dth", "hat", "sth", "thi", "oft", "ion", "ter", "res", "ere",
            "con", "ver", "all", "his", "ate", "ons", "ted", "tho", "nth", "int",
            "est", "hen", "rea", "pro", "out", "are", "oun", "ill", "our", "eve",
            "era", "hes", "ati", "ear", "ain", "ess", "ith", "ted", "ers", "one",
            "ast", "not", "ati", "eve", "tio", "rat", "ere", "ell", "end", "act",
        ]

    # Set the list of possible genre titles for search in description lrt.lt/tema/filmai
    list_of_genres_mediateka: list[str] = [
        'komedija', 'drama', 'trileris', 'nuotykių', 'elito', 'vaidybinis',
        'pramoginis', 'trumpametražis', 'dokumentinis', 'spektaklis', 'naujienos',
        'apybraiža'
    ]

    # Set sample SQL queries, that apper in GUI Combobox
    sample_queries: list[str] = [
        "SELECT * FROM movies WHERE genre = 'komedija';",
        "SELECT * FROM movies WHERE duration > 90;",
        "SELECT * FROM movies WHERE release_year < 1970;",
        "SELECT * FROM movies WHERE description LIKE '%nuotykių%';",
        "SELECT * FROM movies WHERE title LIKE '%dokumentinis%';",
        "SELECT * FROM movies WHERE description LIKE '%dokumentinis%';",
        "SELECT * FROM movies;",
        "SELECT * FROM movies WHERE url IN (SELECT url FROM movies GROUP BY url HAVING COUNT(url) > 1);",
        "SELECT * FROM movies WHERE title IN (SELECT title FROM movies GROUP BY title HAVING COUNT(title) > 1);"
    ]