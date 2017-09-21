import os

from pokemon_scraper.db import PokemonDB
from pokemon_scraper.helpers import make_soup, get_page

DB_NAME  = os.getenv("POKEDEX_DB_NAME")
DB_USER  = os.getenv("POKEDEX_DB_USER")
DB_PASS  = os.getenv("POKEDEX_DB_PASSWORD")

def get_all_pokemons():

    pokedex_page    = get_page("/pokedex/national")
    pokedex         = make_soup(pokedex_page)
    pokemons        = pokedex.find_all("span", class_="infocard-tall")
    pokemon_info    = {"stats": {}}

    for pokemon in pokemons:
        pokemon_details_url  = pokemon.find(class_="ent-name").get("href")
        pokemon_details_page = get_page(pokemon_details_url)
        pokemon_details_soup = make_soup(pokemon_details_page)

        ## "Pokedex Data" Column from /pokedex/{pokemon_name}
        top_panel = pokemon_details_soup.find_all(class_="svtabs-panel-list")[0]
        top_panel = top_panel.find("li")
        top_panel = list(top_panel.children)

        pokedex_data = top_panel[1].find_all(class_="col")[1].find("table")

        pokemon_name    = pokemon_details_soup.find("h1").text
        pokemon_number  = pokedex_data.find("strong").text
        pokemon_jp_name = pokedex_data.find_all("tr")[-1].find("td").string

        if pokemon_jp_name == None:
           pokemon_jp_name = pokemon_name

        # Extract pokemon types
        pokemon_types   = pokedex_data.find_all(class_="type-icon")
        pokemon_types   = [p_type.text.lower() for p_type in pokemon_types]

        # "Base Stats" Column on the bottom right
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

        pokemon_bio = pokemon_details_soup.find_all("h2")[5].next_sibling.next_sibling
        pokemon_bio = pokemon_bio.find("td").string

        pokemon_info["number"]  = "#{}".format(pokemon_number)
        pokemon_info["name"]    = pokemon_name.lower()
        pokemon_info["jp_name"] = pokemon_jp_name.lower()
        pokemon_info["types"]   = ",".join(pokemon_types)
        pokemon_info["bio"]     = pokemon_bio

        yield pokemon_info

def main():

    db = PokemonDB(DB_NAME, DB_USER, DB_PASS)

    print("Connecting to the database ...")
    db.connect()
    print("Connected !")

    print("Clearing Existing Data ...")
    db.delete_all_pokemons()
    print("Data Cleared !")

    print("Creating table ...")
    db.create_pokemons_table()
    print("Table successfully created !")

    print("Saving pokemons ...")
    for pokemon in get_all_pokemons():
        db.insert_pokemon(pokemon)
        print("{} saved !".format(pokemon["name"]))

    db.close_connection()
    print("All Done !!")

if __name__ == "__main__":
    main()
