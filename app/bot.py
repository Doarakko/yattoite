import os
import logging
import random
import time

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from db import Database
import freee
from message import Message


logging.basicConfig(level=logging.WARNING)


app = App(token=os.environ["SLACK_BOT_TOKEN"])
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


@app.message("^.*<@{}>.*$".format(os.environ["SLACK_USER_ID"]))
def message(message):
    m = Message()
    row = m.get_by_random()

    if freee.is_working():
        return

    # camouflage to avoid being identified as a bot
    time.sleep(
        random.choices(
            [10, 20, 30, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600],
            [3, 3, 3, 5, 5, 5, 3, 3, 1, 1, 1, 1, 1],
        )[0]
    )

    client.chat_postMessage(channel=message["channel"], text=row.body)


if __name__ == "__main__":
    Database.initialise()

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
