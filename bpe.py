# bpe.py
import json
from math import inf
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
            for token in line.split():
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
                yield unicodedata.normalize(normalisation, datum["text"])
                
    
    def train(self, vocab_size, cache_trained_bpe=True, cached_bpe_path="trained_bpe.json"):
        """
        Train the BPE model.
        
        Args:
            vocab_size (int): The target vocabulary size.
            cache_trained_bpe (bool): Whether to cache the trained BPE merges.
            cached_bpe_path (str): Path to cache the trained BPE merges.
        """
        if cache_trained_bpe:
            try:
                with open(cached_bpe_path, "r") as f:
                    # Load the list from json
                    saved_merges = json.load(f)
                    
                    # Rebuild the dictionary with tuple keys
                    self.merges = {(t1, t2): rank for t1, t2, rank in saved_merges}
                print("Loaded trained BPE from cache")
                return
            except FileNotFoundError:
                print("No cache found. Starting training...")
                pass
        
        num_merge = vocab_size - len(self.vocab) # to get the number of merges we can do
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
        
        if cache_trained_bpe:
            with open(cached_bpe_path, "w") as f:
                # Convert the Tuple-keyed dict into a safe List of Lists
                # because JSON doesn't support tuple keys
                merges_to_save = [[t1, t2, rank] for (t1, t2), rank in self.merges.items()]
                json.dump(merges_to_save, f)
        

    def __merge(self, t1, t2):
        """
        naviely merge all occurrences of t1 and t2 in word tuples.
        
        Args:
            t1, t2: Tuple elements to merge
        """
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
        """
        Naive update pairs counter based on current word frequencies.
        
        Returns:
            Updated pairs counter
        """
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
        word_map = {}
        output_lines = []
        for line in self.__read_jsonl(input_file):
            encoded_sentence = []
            for token in line.split():
                
                if token not in word_map:
                    word_tuple = tuple(token + "_")
                    word_map[token] = self.__encode_word(word_tuple)
                
                encoded_sentence.append(" ".join(word_map[token]))
            
            output_lines.append(" ".join(encoded_sentence))
            
        # Join everything at the very end
        return "\n".join(output_lines) + "\n"
    
    def __encode_word(self, word):
        """
        Encode a single word using the trained BPE model.
        
        Args:
            word: Tuple of characters representing a word
            
        Returns:
            List of BPE tokens for the word
        """

        word = list(word)

       
       # nothing to merge if word is a single char
        while len(word) > 1:
            new_word = []
            pairs = {}
            i = 0
            j = 0
            while i < len(word) - 1:
                pairs[(word[i], word[i + 1])] = self.merges.get((word[i], word[i + 1]), float('inf'))
                i += 1

            min_pair = min(pairs, key=pairs.get)
            if pairs[min_pair] == float('inf'):
                break

            while j < len(word):
                if j == len(word) - 1:
                    new_word.append(word[j])
                    break
                
                if word[j] == min_pair[0] and word[j + 1] == min_pair[1]:
                    new_word.append(min_pair[0] + min_pair[1])
                    j += 2
                else:
                    new_word.append(word[j])
                    j += 1
            word = new_word
        
        return tuple(word)
                
    
    def decode(self, tokens):
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--encode_file", type=str, required=True)
    parser.add_argument("--vocab_size", type=int, default=1000)
    parser.add_argument("--cache_trained_bpe", type=bool, default=True)
    parser.add_argument("--cached_bpe_path", type=str, default="trained_bpe.json")
    args = parser.parse_args()
    bpe = BPE(args.input_file)
    bpe.train(args.vocab_size, cache_trained_bpe=args.cache_trained_bpe, cached_bpe_path=args.cached_bpe_path)
    
    result = bpe.encode(args.encode_file)
    with open(args.output_file, "w") as f:
        f.write(result)
    
