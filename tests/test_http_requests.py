from unittest.mock import patch
from pokemon_scraper.exceptions import RequestError
from pokemon_scraper.helpers import get_page
import requests
import unittest

class TestHTTP(unittest.TestCase):

    def test_get_page_success(self):

        with patch.object(requests, 'get') as get_page_mock:
            get_page_mock.return_value.status_code = 200
            get_page_mock.return_value.text = "Success !"

            page_data = get_page("/pokedex/pikachu")

            ## Assert that requests was called with the correct url
            get_page_mock.assert_called_with("https://pokemondb.net/pokedex/pikachu")

            self.assertEqual(page_data, "Success !")

    def test_get_page_not_found(self):

        with patch.object(requests, 'get') as get_page_mock:

            get_page_mock.return_value.status_code = 404

            with self.assertRaises(RequestError) as context:
                page_data = get_page("/pokedex/lkerjewkjek")

            self.assertEqual(context.exception.error_code, 404)
            self.assertEqual(context.exception.error_message, "Page not found.")

    def test_get_server_error(self):

        with patch.object(requests, 'get') as get_page_mock:

            get_page_mock.return_value.status_code = 503

            with self.assertRaises(RequestError) as context:
                page_data = get_page("/pokedex/pikachu")

            self.assertEqual(context.exception.error_code, 503)
            self.assertEqual(context.exception.error_message, "Server Error.")
