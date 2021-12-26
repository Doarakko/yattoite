import os
import sys

sys.path.append(os.path.abspath("."))
from db import Database
from message import Message
from freee import FreeeAccessToken, FreeeUser

if __name__ == "__main__":
    Database.initialise()
    message = Message()
    message.create_table()

    freee_access_token = FreeeAccessToken()
    freee_access_token.create_table()

    freee_user = FreeeUser()
    freee_user.create_table()
