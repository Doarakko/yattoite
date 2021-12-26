import os
from psycopg2 import pool


class Database:
    __connection_pool = None

    @classmethod
    def initialise(cls):
        cls.__connection_pool = pool.SimpleConnectionPool(
            dsn=os.environ["DATABASE_URL"], minconn=2, maxconn=10
        )

    @classmethod
    def get_connection(cls):
        return cls.__connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        Database.__connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        Database.__connection_pool.closeall()


class Cursor:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = Database.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, excexption_type, excexption_value, excexption_tb):
        if excexption_value is not None:
            self.connection.rollback()
        else:
            self.cursor.close()
            self.connection.commit()

        Database.return_connection(self.connection)
