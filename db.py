import psycopg2
import sys

class PokemonDB(object):

    def __init__(self, db_name, db_user, db_pass, db_host="localhost", db_port=5432):
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_host = db_host
        self.db_port = db_port

    def connect(self):

        try:
            self.conn = psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_pass)
        except Exception as e:
            sys.exit("Could not connect to the database. Invalid credentials")
        else:
            return self.conn

    def close_connection(self):
        self.conn.close()

    def create_pokemons_table(self):

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

        self.conn.cursor().execute(query)

        self.conn.commit()

    def insert_pokemon(self, pokemon):

        query   = """
        INSERT INTO pokemons ( number, name, jp_name, types, hp, attack, defense,
        sp_atk, sp_def, speed, bio)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            self.conn.cursor().execute(query,(
                       pokemon["number"], pokemon["name"], pokemon["jp_name"],
                       pokemon["types"], pokemon["stats"]["hp"],
                       pokemon["stats"]["attack"], pokemon["stats"]["defense"],
                       pokemon["stats"]["sp_atk"], pokemon["stats"]["sp_def"],
                       pokemon["stats"]["speed"], pokemon["bio"]))

        except KeyError as e:
            sys.exit("Error: Missing {} attribute in pokemon object".format(e))

        except psycopg2.IntegrityError as e:
            error = " ".join(e.pgerror.split())

            if int(e.pgcode) == 23505:
                sys.exit("Insertion Failed: Unique constraint violated. Message: {}".format(error))
        except Exception as e:
            sys.exit(ekkk)

        self.conn.commit()

    def delete_all_pokemons(self):

        self.conn.cursor().execute("DROP TABLE IF EXISTS pokemons;")

