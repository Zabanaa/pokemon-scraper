import requests
from bs4 import BeautifulSoup

POKEDEX_DOMAIN  = "https://pokemondb.net"

def make_soup(html):
    return BeautifulSoup(html, "html.parser")

def get_page(url):

    resp    = requests.get("{}{}".format(POKEDEX_DOMAIN, url))
    status_code = resp.status_code

    if status_code != 200:

        if status_code >= 500 and status_code <= 599 :
            raise RequestError(status_code, "Server Error.")

        if status_code == 404:
            raise RequestError(status_code, "Page not found.")

    return resp.text

