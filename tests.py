from exceptions import RequestError
from main import create_connection, create_table, clear_data, get_page, insert_to_db
from psycopg2.extensions import connection as pg
from unittest.mock import patch

import unittest, os, psycopg2, requests

DB_USER = os.getenv("POKEDEX_SCRAPER_DB_USER")
DB_NAME = os.getenv("POKEDEX_SCRAPER_DB_NAME")
DB_PASS = os.getenv("POKEDEX_SCRAPER_DB_PASS")

class TestDBConnection(unittest.TestCase):

    """
    Test suite for a basic db connection.
    """

    def test_create_connection(self):

        db = create_connection(DB_NAME, DB_USER, DB_PASS)
        self.assertIsInstance(db, pg)
        self.assertIn(DB_USER, db.dsn)
        self.assertIn(DB_NAME, db.dsn)

    def test_failed_connection(self):
        # Test failed connection
        with self.assertRaises(SystemExit) as context:

            db = create_connection("pikachu", "ash", "password123")

        error_msg = "Could not connect to the database. Invalid credentials"
        self.assertEqual(str(context.exception), error_msg)


class TestDBOperations(unittest.TestCase):

    """
    Test suite for database operations.
    """

    def setUp(self):

        self.db = create_connection(DB_NAME, DB_USER, DB_PASS)

        self.pikachu = {
            "number": "#025",
            "name": "pikachu",
            "jp_name": "pikachu",
            "types": "electric",
            "stats":{
                "hp": 34,
                "attack": 34,
                "defense": 34,
                "sp_atk": 34,
                "sp_def": 34,
                "speed": 34,
            },
            "bio": "cute",
            "generation": 1,
        }

        create_table(self.db, "pokemons")

    def test_failed_create_table(self):

        with self.assertRaises(psycopg2.ProgrammingError) as context:
            self.db.cursor().execute("SELECT * FROM pokemon;")

        # 42P01 is the error code for "table [] does not exist"
        error_msg = 'relation "pokemon" does not exist'
        self.assertIn(error_msg, str(context.exception))

    def test_create_table(self):

        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_type='BASE TABLE';
        """

        with self.db.cursor() as cursor:
            cursor.execute(query)
            table_name = cursor.fetchone()

        self.assertEqual("pokemons", table_name[0])

    def test_drop_table(self):

        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_type='BASE TABLE';
        """

        clear_data(self.db, "pokemons")

        with self.db.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

        self.assertIsNone(result)

    def test_insert_to_db(self):

        query = """
        SELECT COUNT(id) FROM pokemons;
        """

        insert_to_db(self.db, self.pikachu)

        with self.db.cursor() as cursor:
            cursor.execute(query)
            row_count = cursor.fetchone()

        self.assertEqual(row_count[0], 1)

    def test_failed_insert_missing_key(self):

        query = """
        SELECT COUNT(id) FROM pokemons;
        """

        del self.pikachu["name"]

        with self.db:

            with self.assertRaises(SystemExit) as context:
                insert_to_db(self.db, self.pikachu)

        error_msg = "Error: Missing 'name' attribute in pokemon object"
        self.assertEqual(str(context.exception), error_msg)

    def test_failed_insert_unique_constraint_violation(self):

        query = """
        SELECT COUNT(id) FROM pokemons;
        """

        with self.db:

            insert_to_db(self.db, self.pikachu)

            with self.assertRaises(SystemExit) as context:
                insert_to_db(self.db, self.pikachu)

            error_message = "Unique constraint violated"
            self.assertIn(error_message, str(context.exception))

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

    def test_get_page_not_found(self):

        with patch.object(requests, 'get') as get_page_mock:

            get_page_mock.return_value.status_code = 503

            with self.assertRaises(RequestError) as context:
                page_data = get_page("/pokedex/pikachu")

            self.assertEqual(context.exception.error_code, 503)
            self.assertEqual(context.exception.error_message, "Server Error.")

if __name__ == "__main__":
    unittest.main()
