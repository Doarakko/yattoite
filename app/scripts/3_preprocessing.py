import argparse
import re
import pandas as pd
import spacy
import swifter


nlp = spacy.load("ja_ginza")

code_regex = re.compile(
    "[!\"#$%&'\\\\()*+,-./:;<=＝>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・•（）＄＃＠。、？！｀＋￥％…←↑→↓]"
)


def preprocessing(row):
    row["body"] = re.sub(":.+:", "", row["body"])
    row["body"] = code_regex.sub("", row["body"])

    doc = nlp(row["body"])
    l = []
    for sent in doc.sents:
        s = ""
        for ent in sent:
            if len(s) == 0:
                s = str(ent)
            else:
                s = "{} {}".format(s, ent)
        l.append(s)

    row["body_with_space"] = "\n".join(l)

    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input file path", default="data/comments.csv")
    parser.add_argument(
        "-o", help="output file path", default="data/preprocessing_comments.csv"
    )

    args = parser.parse_args()
    input_path = args.i
    output_path = args.o

    comments = pd.read_csv(input_path)

    comments = comments[
        (comments["body"].str.contains("<@.*>") == False)
        & (comments["body"].str.contains("```") == False)
        & (comments["body"].str.contains("<#.*>") == False)
        & (comments["body"].str.contains("<!subteam.*>") == False)
        & (comments["body"].str.contains("http") == False)
        & (comments["body"].str.contains("`.+`") == False)
        & (comments["body"].str.contains("&gt;") == False)
        & (comments["body"].str.contains("todo") == False)
        & (comments["body"].str.contains("done") == False)
        & (comments["body"].str.contains("たんじろう") == False)
        & (comments["body"].str.contains("times") == False)
    ]

    comments = comments.swifter.apply(lambda x: preprocessing(x), axis=1)
    comments.to_csv(output_path)
    print("save to {}".format(output_path))
