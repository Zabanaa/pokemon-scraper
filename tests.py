from main import create_connection, create_table
from psycopg2.extensions import connection as pg

import unittest, os, psycopg2

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

    def test_failed_connection(self):
        # Test failed connection
        with self.assertRaises(SystemExit) as context:

            db = create_connection("pikachu", "ash", "password123")

        error_msg = "Could not connect to the database. Invalid credentials"
        self.assertEqual(str(context.exception), error_msg)

    def test_failed_create_table(self):
        db = create_connection(self.db_name, self.db_user, self.db_pass)
        self.assertIsInstance(db, pg)

        with db:

            table = create_table(db, "pokemons")

            with db.cursor() as cursor:

                with self.assertRaises(psycopg2.ProgrammingError) as context:
                    cursor.execute("SELECT * FROM pokemon;")

                # 42P01 is the error code for "table [] does not exist"
                self.assertEqual("42P01", context.exception.pgcode)

    def test_create_table(self):
        db = create_connection(self.db_name, self.db_user, self.db_pass)

        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_type='BASE TABLE';
        """

        with db:
            table = create_table(db, "pokemons")

            with db.cursor() as cursor:
                cursor.execute(query)
                table_name = cursor.fetchone()

            self.assertEqual("pokemons", table_name[0])

if __name__ == "__main__":
    unittest.main()
