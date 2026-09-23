import mariadb
from config import Config
import logging

logger = logging.getLogger(__name__)



class DatabaseClient:

    def __init__(self):
        self.connection = mariadb.connect(
            host=Config.get("DB_HOST"),
            port=int(Config.get("DB_PORT")),
            user=Config.get("DB_USER"),
            password=Config.get("DB_PASSWORD"),
            database=Config.get("DB_NAME"),
        )

        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, parameters=None):
        if parameters:
            self.cursor.execute(query, parameters)
        else:
            self.cursor.execute(query)
        logger.info("DB QUERY | executed")


    def fetch_one(self):
        return self.cursor.fetchone()

    def fetch_all(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
