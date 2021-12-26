import argparse
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("user_id", help="slack user id")

    args = parser.parse_args()
    user_id = args.user_id

    comments = pd.read_csv("data/comments.csv")

    comments = comments[(comments["subtype"].isnull()) & (comments["user"] == user_id)]
    comments.to_csv("data/{}_comments.csv".format(user_id))
