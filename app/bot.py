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

    # camouflage to avoid being identified as a bot
    time.sleep(
        random.choices(
            [10, 20, 30, 60] + list(range(180, 601, 60)), [1, 2, 3, 3] + [1] * 8
        )
    )
    say(row.body)


if __name__ == "__main__":
    Database.initialise()

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
