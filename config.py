class Config:

    # Set databases
    database_epika = "epika_movies.db"
    database_mediateka = "mediateka_movies.db"

    # Set up Chrome driver options (--headless if False)
    show_browser: bool = False

    # Set epika.lrt.lt page content lazy loading speed - scroll step and wait time in between
    lazy_scroll_step: int = 500
    wait_time: int = 0.5

    # Set logging level for logging module
    logging_level = "INFO"

    # Set how many epika.lrt.lt search pages results to scrape by stetting search strings in list
    list_search_strings_epika: list[str] = ["Komedija"]

    """Lithuanian_trigrams [
        "ant", "ing", "tai", "kur", "dži",
        "sta", "gal", "sav", "pav", "tar",
        "tik", "lab", "vis", "ger", "tie",
        "nie", "art", "met", "kas", "tuo",
        "jau", "būt", "vak", "dar", "man",
        "sen", "aps", "tik", "ėjo", "nes",
        "vie", "lia", "jim", "ten", "jos",
        "šio", "dėl", "kit", "dar", "kai",
        "pas", "sak", "prie", "min", "tur",
        "kie", "buv", "mat", "toj", "ką*",
        "tam", "žmo", "pri", "pat", "dir"
    ]
    """

    """Lithuanian_bigrams [
        "pa*", "pr*", "ne*", "ka*", "te*", 
        "na*", "jo*", "ap*", "da*", "ja*", 
        "is*", "ta*", "ma*", "ti*", "ju*", 
        "no*", "ko*", "su*", "sa*", "ki*", 
        "me*", "ga*", "to*", "la*", "gr*", 
        "po*", "ge*", "di*", "at*", "ba*", 
        "nu*", "se*", "vi*", "ku*", "mi*", 
        "tr*", "pi*", "st*", "va*", "ie*", 
        "ma*", "ri*", "le*", "ra*", "ar*", 
        "am*", "tu*", "re*", "bu*", "as*", 
        "de*", "an*", "ir*", "al*", "mo*"
    ]
    """

    """Lithuanian_letters_and_numbers [
        "a**", "ą**", "b**", "c**", "č**", 
        "d**", "e**", "ę**", "ė**", "f**", 
        "g**", "h**", "i**", "į**", "y**", 
        "j**", "k**", "l**", "m**", "n**", 
        "o**", "p**", "r**", "s**", "š**", 
        "t**", "u**", "ų**", "ū**", "v**", 
        "z**", "ž**", "0**", "1**", "2**", 
        "3**", "4**", "5**", "6**", "7**", 
        "8**", "9**"
    ]
    """
    """English_trigrams [
        "the", "and", "ing", "her", "ere", "ent", "tha", "nth", "was", "eth",
        "for", "dth", "hat", "sth", "thi", "oft", "ion", "ter", "res", "ere",
        "con", "ver", "all", "his", "ate", "ons", "ted", "tho", "nth", "int",
        "est", "hen", "rea", "pro", "out", "are", "oun", "ill", "our", "eve",
        "era", "hes", "ati", "ear", "ain", "ess", "ith", "ted", "ers", "one",
        "ast", "not", "ati", "eve", "tio", "rat", "ere", "ell", "end", "act"
    ]
    """
    # Set the list of possible genre titles to search in description for lrt.lt/tema/filmai
    list_of_genres_mediateka = [
        'komedija', 'drama', 'trileris', 'nuotykių', 'elito', 'vaidybinis',
        'pramoginis', 'trumpametražis', 'dokumentinis', 'spektaklis', 'naujienos',
        'apybraiža'
    ]

    sample_queries = [
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

    # Set scrape mediateka first_page or all