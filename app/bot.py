import os
import logging
import random
import time

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from db import Database
import freee
from message import Message


logging.basicConfig(level=logging.WARNING)


app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.message("^.*<@{}>.*$".format(os.environ["SLACK_USER_ID"]))
def message(say):
    message = Message()
    row = message.get_by_random()

    if freee.is_working():
        return

    time.sleep(
        random.choice(
            [10, 20, 20, 30, 30, 30, 60, 60, 60, 180, 240, 300, 360, 420, 480, 540, 600]
        )
    )
    say(row.body)


if __name__ == "__main__":
    Database.initialise()
    freee.initialise()

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
