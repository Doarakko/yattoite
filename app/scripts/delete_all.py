import os
import sys

sys.path.append(os.path.abspath("."))
from db import Database
from message import Message

if __name__ == "__main__":
    Database.initialise()
    message = Message()
    message.delete_all()
