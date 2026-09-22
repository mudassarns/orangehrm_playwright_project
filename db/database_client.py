import mariadb
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseClient:

    def __init__(self):
        self.connection = mariadb.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
        )

        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, parameters=None):
        if parameters:
            self.cursor.execute(query, parameters)
        else:
            self.cursor.execute(query)

    def fetch_one(self):
        return self.cursor.fetchone()

    def fetch_all(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
