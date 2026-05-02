# bpe.py
import json
from pickle import FALSE
import unicodedata 
from collections import Counter, defaultdict
import argparse

class BPE:
    def __init__(self, input_file):
        self.merges = {}
        self.pairs = Counter()
        self.vocab = set()
        self.word_freq = defaultdict(int)
        line_generator = self.__read_jsonl(input_file)
        
        for line in line_generator:
            for token in line:
                chars = tuple(token + "_")
                self.word_freq[chars] += 1
        
        for word_tuple, freq in self.word_freq.items():
            self.vocab.update(word_tuple)
            for i in range(len(word_tuple) - 1):
                self.pairs[(word_tuple[i], word_tuple[i + 1])] += freq
                
    def __read_jsonl(self, input_file, normalisation="NFC"):
        """
        Read JSONL file as a generator that yields pretokenised lines one line at a time
        """
        with open(input_file, "r") as f:
            for line in f:
                datum = json.loads(line)
                yield unicodedata.normalize(normalisation, datum["text"]).split()
                
    
    def train(self, num_merge):
        for k in range(num_merge):
            if not self.pairs:
                print(f"ran out of pairs at merge {k}!")
                break
            # Reconstruct pairs from word_freq
            # most_common(1) returns [((t1, t2), count)]
            t1, t2 = self.pairs.most_common(1)[0][0]
            # merge stores the priority so the right merge is applied. Use a dict for O(1)
            self.merges[(t1, t2)] = k
            self.__merge(t1, t2)

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
    
    def encode(self, input_file):
        """
        Encode text using the trained BPE model.
        
        Args:
            input_file: Path to the input file containing text
            
        Returns:
            Encoded tokens
        """
        #normalise text to get rid of unicode variations
        line_generator = self.__read_jsonl(input_file)
        word_map = {}
        for word_tuple, freq in word_freq.items():
            word_map[" ".join(word_tuple)] = self.__encode_word(word_tuple)
        
        output = ""
        for line in corpus:
            tokens = line.split()
            for token in tokens:
                if token in word_map:
                    output += " ".join(word_map[token]) + " "
            output = output.strip() + "\n"
        return output
    
    def decode(self, tokens):
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
    
