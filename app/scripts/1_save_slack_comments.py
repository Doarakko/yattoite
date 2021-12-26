import argparse
import datetime
import os
import time
import pandas as pd
from slack_sdk import WebClient


client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def get_channels(q):
    df = pd.DataFrame(index=[], columns=["id", "name"])
    has_more = True
    cursor = None

    while has_more:
        try:
            response = client.conversations_list(limit=1000, cursor=cursor)
            time.sleep(1)

            for i in response["channels"]:
                if i["name"].find(q) != -1:
                    id = i["id"]
                    name = i["name"]
                    record = pd.Series([id, name], index=df.columns)
                    df = df.append(record, ignore_index=True)

            has_more = response["has_more"]
            cursor = response["next_cursor"]
        except Exception as e:
            print("got an error: {}".format(e))
            time.sleep(60)

    return df


def get_comments(channel_id):
    df = pd.DataFrame(
        index=[],
        columns=[
            "type",
            "subtype",
            "body",
            "user",
            "reaction_count",
            "timestamp",
            "created",
        ],
    )
    has_more = True
    cursor = None

    while has_more:
        try:
            response = client.conversations_history(
                channel=channel_id, cursor=cursor, limit=100
            )
            time.sleep(1)

            for i in response["messages"]:
                type = i["type"]
                body = i["text"]

                subtype = i["subtype"] if "subtype" in i else None
                user = i["user"] if "user" in i else None
                reaction_count = count_reactions(i)
                timestamp = i["ts"] if "ts" in i else None
                created = (
                    datetime.datetime.fromtimestamp(float(timestamp))
                    if "ts" in i
                    else None
                )

                record = pd.Series(
                    [type, subtype, body, user, reaction_count, timestamp, created],
                    index=df.columns,
                )
                df = df.append(record, ignore_index=True)

            has_more = bool(response["has_more"])
            cursor = response["response_metadata"]["next_cursor"]
        except Exception as e:
            print("got an error: {}".format(e))
            time.sleep(60)

    return df


def count_reactions(row):
    if "reactions" not in row:
        return 0

    count = 0
    for i in row["reactions"]:
        count += i["count"]

    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("q", help="query")
    args = parser.parse_args()

    channels = get_channels(q=args.q)
    print("get {} times channes".format(len(channels)))

    channels.to_csv("data/times_channels.csv")
    print("save times channes to csv")

    comments = pd.DataFrame(
        index=[],
        columns=[
            "type",
            "subtype",
            "body",
            "user",
            "reaction_count",
            "timestamp",
            "created",
        ],
    )
    for i, row in channels.iterrows():
        df = get_comments(row["id"])
        df.to_csv("data/comments_{}.csv".format(row["name"]))

        comments = pd.concat([comments, df])
        print("get {} comments in {}".format(len(df), row["name"]))

    comments.to_csv("data/comments.csv")
    print("save comments to csv")
