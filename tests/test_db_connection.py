import unittest
from psycopg2.extensions import connection as pg
from pokemon_scraper.db import PokemonDB
from .config import DB_NAME, DB_USER, DB_PASS

class TestDBConnection(unittest.TestCase):

    """
    Test suite for a basic db connection.
    """

    def test_create_connection(self):

        db = PokemonDB(DB_NAME, DB_USER, DB_PASS)
        connection = db.connect()
        self.assertIsInstance(connection, pg)
        self.assertIn(DB_USER, connection.dsn)
        self.assertIn(DB_NAME, connection.dsn)

    def test_failed_connection(self):
        # Test failed connection
        with self.assertRaises(SystemExit) as context:

            db          = PokemonDB("pikachu", "ash", "password123")
            connection  = db.connect()

        error_msg = "Could not connect to the database. Invalid credentials"
        self.assertEqual(str(context.exception), error_msg)

