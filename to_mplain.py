import argparse
import nltk
nltk.download('punkt')

def reformat_text_to_mplain(text):
    text = text.split("\n\n")
    text = [paragraph.replace("\n", " ") for paragraph in text]

    text = [nltk.tokenize.sent_tokenize(paragraph) for paragraph in text]

    text = ["\n".join(paragraph) for paragraph in text]

    text = "\n\n".join(text)
    
    return text


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="filename of text to make into mplain format")
    parser.add_argument("-o", "--output", help="output filename")

    args = parser.parse_args()

    with open(args.filename, "r") as f:
        text = f.read()
    
    text = reformat_text_to_mplain(text)

    with open(args.output, "w") as f:
        f.write(text)
