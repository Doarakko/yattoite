import argparse
import markovify


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input file path", default="data/sentences.txt")
    parser.add_argument("-o", help="output file path", default="data/output.txt")
    parser.add_argument("-n", help="count of generate sentences", default=10, type=int)
    parser.add_argument("-s", help="state size", default=2, type=int)

    args = parser.parse_args()
    input_path = args.i
    output_path = args.o
    n = args.n
    state_size = args.s

    with open(input_path) as f:
        text = f.read()

    text_model = markovify.NewlineText(text, well_formed=False, state_size=state_size)

    with open(output_path, mode="w") as f:
        for i in range(n):
            s = text_model.make_sentence()
            if s is None:
                continue

            s = s.replace(" ", "")
            f.write(s + "\n")

        print("save to {}".format(output_path))
