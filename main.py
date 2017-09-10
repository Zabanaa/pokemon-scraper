import os, sys
import requests
import psycopg2
from bs4 import BeautifulSoup

POKEDEX_DOMAIN  = "https://pokemondb.net"

DB_NAME         = os.getenv("POKEDEX_DB_NAME")
DB_USER         = os.getenv("POKEDEX_DB_USER")
DB_PASS         = os.getenv("POKEDEX_DB_PASSWORD")
DB_HOST         = os.getenv("POKEDEX_DB_HOST")
DB_PORT         = os.getenv("POKEDEX_DB_PORT")

def create_connection():
    try:
        db  = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS,
                               host=DB_HOST, port=DB_PORT)
    except Exception as e:
        sys.exit("Error Connecting to the Database")
    else:
        return db

def clear_data(cursor):
    cursor.execute("TRUNCATE TABLE pokemons;")

def create_table(cursor):
    query  = """
            CREATE TABLE IF NOT EXISTS pokemons (
                id SERIAL PRIMARY KEY,
                number CHAR(10) NOT NULL,
                name CHAR(255) NOT NULL,
                jp_name CHAR(255) NOT NULL,
                types CHAR(255) NOT NULL,
                hp INT NOT NULL,
                attack INT NOT NULL,
                defense INT NOT NULL,
                sp_atk INT NOT NULL,
                sp_def INT NOT NULL,
                speed INT NOT NULL,
                bio TEXT NOT NULL,
                generation INT,
                CONSTRAINT unique_name UNIQUE (name)
            );
            """

    cursor.execute(query)

def insert_to_db(cursor, pokemon):
    query   = """
            INSERT INTO pokemons (
                number,
                name,
                jp_name,
                types,
                hp,
                attack,
                defense,
                sp_atk,
                sp_def,
                speed,
                bio
            )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

    cursor.execute(query,(
                   pokemon["number"], pokemon["name"], pokemon["jp_name"],
                   pokemon["types"], pokemon["stats"]["hp"],
                   pokemon["stats"]["attack"], pokemon["stats"]["defense"],
                   pokemon["stats"]["sp_atk"], pokemon["stats"]["sp_def"],
                   pokemon["stats"]["speed"], pokemon["bio"]))



def make_soup(url):
    resp    = requests.get("{}{}".format(POKEDEX_DOMAIN, url))
    return BeautifulSoup(resp.text, "html.parser")

def get_all_pokemons():

    pokedex         = make_soup("/pokedex/national")
    pokemons        = pokedex.find_all("span", class_="infocard-tall")
    pokemon_info    = {"stats": {}}

    for pokemon in pokemons:
        pokemon_details_url  = pokemon.find(class_="ent-name").get("href")
        pokemon_details_page = make_soup(pokemon_details_url)

        ## "Pokedex Data" Column from /pokedex/{pokemon_name}
        top_panel = pokemon_details_page.find_all(class_="svtabs-panel-list")[0]
        top_panel = top_panel.find("li")
        top_panel = list(top_panel.children)

        pokedex_data = top_panel[1].find_all(class_="col")[1].find("table")

        pokemon_name    = pokemon_details_page.find("h1").text
        pokemon_number  = pokedex_data.find("strong").text
        pokemon_jp_name = pokedex_data.find_all("tr")[-1].find("td").string

        if pokemon_jp_name == None:
            pokemon_jp_name = pokemon_name

        ## Extract pokemon types
        pokemon_types   = pokedex_data.find_all(class_="type-icon")
        pokemon_types   = [p_type.text.lower() for p_type in pokemon_types]

        ## "Base Stats" Column on the bottom right

        base_stats  = top_panel[3]
        base_stats  = base_stats.find(class_="col").find("table").find("tbody")
        base_stats  = base_stats.find_all("tr")


        for stat in base_stats:

            if any([
                    stat.find("th") is None,
                    stat.find(class_="num") is None
            ]):
                continue

            title = stat.find("th").string.lower().replace(" ", "").replace(".", "_")
            value = stat.find(class_="num").string
            pokemon_info["stats"][title] = value

        pokemon_bio = pokemon_details_page.find_all("h2")[5].next_sibling.next_sibling
        pokemon_bio = pokemon_bio.find("td").string

        pokemon_info["number"]  = pokemon_number
        pokemon_info["name"]    = pokemon_name
        pokemon_info["jp_name"] = pokemon_jp_name
        pokemon_info["types"]   = pokemon_types
        pokemon_info["bio"]     = pokemon_bio

        yield pokemon_info


def main():

    # for pokemon in get_all_pokemons():
    #     print("Done ")
    #     print()

    print("Connecting to the database ...")
    db = create_connection()
    print("Connected !")

    with db:

        with db.cursor() as cursor:

            print("Clearing Existing Data ...")
            clear_data(cursor)
            print("Data Cleared !")

            print("Creating table ...")
            create_table(cursor)
            print("Table successfully created !")

            db.commit()

            print("Saving pokemons ...")
            for pokemon in get_all_pokemons():

                try:
                    insert_to_db(cursor, pokemon)
                except psycopg2.ProgrammingError as e:
                    sys.exit("Error: {}".format(e))

                print("{} saved !".format(pokemon["name"]))

            cursor.close()

        db.commit()

    print("All Done !!")

if __name__ == "__main__":
    main()
