import argparse
import os
import sys

sys.path.append(os.path.abspath("."))
from db import Database
from message import Message

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input file path", default="data/output.txt")

    args = parser.parse_args()
    input_path = args.i

    Database.initialise()
    message = Message()
    with open(input_path) as f:
        list = []
        for line in f:
            t = (line,)
            list.append(t)

        message.adds(list)
