# bpe.py
import json
from pickle import FALSE
from unicodedata import normalize
from collections import Counter, defaultdict
import argparse

class BPE:
    def __init__(self, input_file):
        self.merges = []
        self.pairs = Counter()
        self.vocab = set()
        self.word_freq = defaultdict(int)
        with open(input_file, "r") as f:
            for line in f:
                datum = json.loads(line)
                text_split = (normalize("NFC", datum["text"])).split()
                for token in text_split:
                    chars = tuple(token + "_")
                    self.word_freq[chars] += 1
        
        for word_tuple, freq in self.word_freq.items():
            self.vocab.update(word_tuple)
            for i in range(len(word_tuple) - 1):
                self.pairs[(word_tuple[i], word_tuple[i + 1])] += freq
        
    def train(self, num_merge):
        for k in range(num_merge):
            if not self.pairs:
                print(f"ran out of pairs at merge {k}!")
                break
            # Reconstruct pairs from word_freq
            # most_common(1) returns [((t1, t2), count)]
            t1, t2 = self.pairs.most_common(1)[0][0]
            self.merges.append((t1, t2))
            self.__merge(t1, t2)
    
        pass
    
    def __merge(self, t1, t2):
        new_word_freq = defaultdict(int)
        for word_tuple, freq in self.word_freq.items():
            i = 0
            new_word = []
            while i < len(word_tuple):
                if i < len(word_tuple) - 1 and word_tuple[i] == t1 and word_tuple[i + 1] == t2:
                    new_word.append(t1 + t2)
                    i += 2
                else:
                    new_word.append(word_tuple[i])
                    i += 1
            new_word_freq[tuple(new_word)] = freq

        self.word_freq = new_word_freq
        self.pairs = self.__update_pairs()
        
    
    def __update_pairs(self):
        pairs = Counter()
        for word_tuple, freq in self.word_freq.items():
            for i in range(len(word_tuple) - 1):
                pairs[(word_tuple[i], word_tuple[i + 1])] += freq
        return pairs
    
    def encode():
        pass
    
    def decode():
        pass
    
    # def __merge(self, t1, t2):
    #     self.vocab.add(t1 + t2)
    #     # Can't mutate the dict while iteratingg
    #     new_word_freq = defaultdict(int)
    #     for word_tuple, freq in self.word_freq.items():
    #         i = 0
    #         new_word = []
    #         while (i < len(word_tuple)):
    #             if i == len(word_tuple) - 1:
    #                 # handle last char
    #                 new_word.append(word_tuple[i])
    #                 break
                
    #             if word_tuple[i] == t1 and word_tuple[i + 1] == t2:
    #                 if (i - 1) >= 0:
    #                     # update pairs to remove old pair and add new pair
    #                     self.pairs[word_tuple[i - 1], t1] -= freq
    #                     self.pairs[(word_tuple[i - 1], t1 + t2)] += freq
    #                 if (i + 2) < len(word_tuple):
    #                     # update pairs to remove old pair and add new pair
    #                     self.pairs[t2, word_tuple[i + 2]] -= freq
    #                     self.pairs[(t1 + t2, word_tuple[i + 2])] += freq
                    
    #                 new_word.append(t1 + t2)
    #                 # We use subtraction instead of popping here to handle the aaa edge case
    #                 self.pairs[(t1, t2)] -= freq
    #                 # Skip both chars consumed
    #                 i += 2
    #             else:
    #                 new_word.append(word_tuple[i])
    #                 i += 1
    #         new_word_freq[tuple(new_word)] = freq
        
    #     self.word_freq = new_word_freq
        
    #     #strip away the 0 counts
    #     self.pairs = +self.pairs
        


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--file", type=str, required=True)
    # args = parser.parse_args()
    bpe = BPE("data/xho/train.jsonl")
    bpe.train(1000)
    print(bpe.merges)
    
