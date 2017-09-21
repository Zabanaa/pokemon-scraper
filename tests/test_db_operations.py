import unittest
import psycopg2
from .config import DB_NAME, DB_USER, DB_PASS
from pokemon_scraper.db import PokemonDB

class TestDBTables(unittest.TestCase):

    def setUp(self):

        self.db = PokemonDB(DB_NAME, DB_USER, DB_PASS)
        self.conn = self.db.connect()

    def test_create_table(self):

        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_type='BASE TABLE';
        """

        with self.db.conn.cursor() as cursor:
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

        self.db.delete_all_pokemons()

        with self.db.conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

        self.assertIsNone(result)

class TestDBOperations(unittest.TestCase):

    """
    Test suite for database operations.
    """

    def setUp(self):

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

        self.db = PokemonDB(DB_NAME, DB_USER, DB_PASS)
        self.conn = self.db.connect()

        self.db.delete_all_pokemons()
        self.db.create_pokemons_table()

    def tearDown(self):
        self.conn.close()

    def test_failed_create_table(self):

        with self.assertRaises(psycopg2.ProgrammingError) as context:
            self.db.conn.cursor().execute("SELECT * FROM pokemon;")

        # 42P01 is the error code for "table [] does not exist"
        error_msg = 'relation "pokemon" does not exist'
        self.assertIn(error_msg, str(context.exception))

    def test_insert_to_db(self):

        query = """
        SELECT COUNT(id) FROM pokemons;
        """

        self.db.insert_pokemon(self.pikachu)

        with self.db.conn.cursor() as cursor:
            cursor.execute(query)
            row_count = cursor.fetchone()

        self.assertEqual(row_count[0], 1)

    def test_failed_insert_missing_key(self):

        query = """
        SELECT COUNT(id) FROM pokemons;
        """

        del self.pikachu["name"]

        with self.db.conn:

            with self.assertRaises(SystemExit) as context:
                self.db.insert_pokemon(self.pikachu)

        error_msg = "Error: Missing 'name' attribute in pokemon object"
        self.assertEqual(str(context.exception), error_msg)

    def test_failed_insert_unique_constraint_violation(self):

        query = """
        SELECT COUNT(id) FROM pokemons;
        """
        self.db.insert_pokemon(self.pikachu)

        with self.assertRaises(SystemExit) as context:
            self.db.insert_pokemon(self.pikachu)

        error_message = "Unique constraint violated"
        self.assertIn(error_message, str(context.exception))

