from main import create_connection
from psycopg2.extensions import connection as pg

import unittest
import os

class TestDB(unittest.TestCase):

    """
    Test class for the DB instance
    """
    def setUp(self):
        self.db_user = os.getenv("POKEDEX_SCRAPER_DB_USER")
        self.db_pass = os.getenv("POKEDEX_SCRAPER_DB_PASS")
        self.db_name = os.getenv("POKEDEX_SCRAPER_DB_NAME")

    def tearDown(self):
        pass

    def test_create_connection(self):

        db = create_connection(self.db_name, self.db_user, self.db_pass)
        self.assertIsInstance(db, pg)
        self.assertIn(self.db_user, db.dsn)
        self.assertIn(self.db_name, db.dsn)

        # Test failed connection
        with self.assertRaises(SystemExit) as context:

            db = create_connection("pikachu", "ash", "password123")

        error_msg = "Could not connect to the database. Invalid credentials"
        self.assertEqual(str(context.exception), error_msg)

    def test_create_table(self):
        pass


if __name__ == "__main__":
    unittest.main()
