import argparse
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", help="input file path", default="data/preprocessing_comments.csv"
    )
    parser.add_argument("-o", help="output file path", default="data/sentences.txt")
    parser.add_argument(
        "-min", help="minimum word count in sentence", default=5, type=int
    )
    parser.add_argument("-max", help="max word count in sentence", default=10, type=int)

    args = parser.parse_args()
    input_path = args.i
    output_path = args.o
    min_word_count = args.min
    max_word_count = args.max

    comments = pd.read_csv(input_path)

    with open(output_path, mode="w") as f:
        for index, row in comments.iterrows():
            sentences = str(row["body_with_space"]).split("\n")
            for i in sentences:
                count = len(i.split())
                if count >= min_word_count and count <= max_word_count:
                    f.write(i + "\n")

        print("save to {}".format(output_path))
