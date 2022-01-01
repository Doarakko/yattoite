import os
import sys

sys.path.append(os.path.abspath("."))
from db import Cursor, Database


if __name__ == "__main__":
    Database.initialise()

    with open("./scripts/init.sql") as f:
        s = f.read()
        with Cursor() as cur:
            cur.execute(s)
