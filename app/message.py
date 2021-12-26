from psycopg2 import extras
from db import Cursor


class Message:
    def __init__(self, body=None):
        self.body = body

    def create_table(self):
        with Cursor() as cur:
            cur.execute(
                "CREATE TABLE messages (\
                        id SERIAL NOT NULL,\
                        body TEXT NOT NULL,\
                        created_at TIMESTAMP DEFAULT NOW(),\
                        updated_at TIMESTAMP DEFAULT NOW(),\
                        PRIMARY KEY (id)\
                    );"
            )

    @classmethod
    def get_by_random(cls):
        with Cursor() as cur:
            cur.execute(
                "SELECT body FROM messages ORDER BY RANDOM() limit 1",
            )
            row = cur.fetchone()

            return cls(
                body=row[0],
            )

    def adds(self, list):
        with Cursor() as cur:
            extras.execute_values(cur, "INSERT INTO messages (body) VALUES %s", list)

    def delete_all(self):
        with Cursor() as cur:
            cur.execute(
                "DELETE FROM messages",
            )
