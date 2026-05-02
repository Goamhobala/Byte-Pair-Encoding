# bpe.py
import json
from unicodedata import normalize
from collections import Counter

def test():
    counts = Counter()
    with open("data/xho/train.jsonl", "r") as f:
        tokens = []
        for line in f:
            datum = json.loads(line)
            text_split = (normalize("NFC", datum["text"])).split()
            for token in text_split:
                temp = token + "_"
                tokens.append(temp)
                counts.update(temp)    
    print(tokens)

if __name__ == "__main__":
    test()
