import json
import tempfile
import os
import unittest
from typing import List
from bpe import BPE
import bpe


def make_jsonl(lines: List[str]) -> str:
    """Write lines as a temp JSONL file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for line in lines:
        f.write(json.dumps({"text": line}) + "\n")
    f.close()
    return f.name


class TestInit(unittest.TestCase):
    def setUp(self):
        # "ab ab c" → tokens: ["ab", "ab", "c"]
        # word_freq: {('a','b','_'): 2, ('c','_'): 1}
        self.path = make_jsonl(["ab ab c"])
        self.bpe = BPE(self.path)

    def tearDown(self):
        os.unlink(self.path)

    def test_word_freq(self):
        self.assertEqual(self.bpe.word_freq[("a", "b", "_")], 2)
        self.assertEqual(self.bpe.word_freq[("c", "_")], 1)

    def test_vocab_contains_chars(self):
        self.assertIn("a", self.bpe.vocab)
        self.assertIn("b", self.bpe.vocab)
        self.assertIn("_", self.bpe.vocab)
        self.assertIn("c", self.bpe.vocab)

    def test_pairs_counts(self):
        # ('a','b') appears twice (freq 2), ('b','_') appears twice
        self.assertEqual(self.bpe.pairs[("a", "b")], 2)
        self.assertEqual(self.bpe.pairs[("b", "_")], 2)
        self.assertEqual(self.bpe.pairs[("c", "_")], 1)

    def test_multiple_lines(self):
        path = make_jsonl(["ab", "ab"])
        bpe = BPE(path)
        os.unlink(path)
        self.assertEqual(bpe.word_freq[("a", "b", "_")], 2)


class TestMerge(unittest.TestCase):
    def setUp(self):
        self.path = make_jsonl(["ab ab c"])
        self.bpe = BPE(self.path)

    def tearDown(self):
        os.unlink(self.path)

    def test_merge_updates_word_freq(self):
        self.bpe._BPE__merge("a", "b")
        self.assertIn(("ab", "_"), self.bpe.word_freq)
        self.assertEqual(self.bpe.word_freq[("ab", "_")], 2)
        self.assertNotIn(("a", "b", "_"), self.bpe.word_freq)

    def test_merge_updates_pairs(self):
        self.bpe._BPE__merge("a", "b")
        # after merge: ("ab","_") pair should exist
        self.assertIn(("ab", "_"), self.bpe.pairs)
        # ("a","b") pair should be gone
        self.assertEqual(self.bpe.pairs[("a", "b")], 0)

    def test_merge_non_adjacent_unchanged(self):
        # 'c_' tuple should not be affected by merging 'a'+'b'
        self.bpe._BPE__merge("a", "b")
        self.assertIn(("c", "_"), self.bpe.word_freq)

    def test_merge_overlapping_aaa(self):
        # "aaa" → ('a','a','a','_')
        # merging ('a','a') should produce ('aa','a','_'), not ('aa','aa','_')
        path = make_jsonl(["aaa"])
        bpe = BPE(path)
        os.unlink(path)
        bpe._BPE__merge("a", "a")
        self.assertIn(("aa", "a", "_"), bpe.word_freq)
        self.assertNotIn(("aa", "aa", "_"), bpe.word_freq)

    def test_merge_single_char_word(self):
        path = make_jsonl(["a"])
        bpe = BPE(path)
        os.unlink(path)
        # only pair is ('a','_') — merging it should yield ('a_',)
        bpe._BPE__merge("a", "_")
        self.assertIn(("a_",), bpe.word_freq)


class TestUpdatePairs(unittest.TestCase):
    def test_pairs_rebuilt_after_merge(self):
        path = make_jsonl(["abc"])
        bpe = BPE(path)
        os.unlink(path)
        # word: ('a','b','c','_'), pairs: a-b, b-c, c-_
        bpe._BPE__merge("a", "b")
        # now word: ('ab','c','_'), pairs should be ab-c, c-_
        self.assertIn(("ab", "c"), bpe.pairs)
        self.assertIn(("c", "_"), bpe.pairs)
        self.assertNotIn(("a", "b"), bpe.pairs)
        self.assertNotIn(("b", "c"), bpe.pairs)


class TestTrain(unittest.TestCase):
    def setUp(self):
        # "aaab" repeated — ('a','a','a','b','_')
        # most frequent pair should be ('a','a') with count 2
        self.path = make_jsonl(["aaab aaab"])
        self.bpe = BPE(self.path)

    def tearDown(self):
        os.unlink(self.path)

    def test_merges_recorded(self):
        self.bpe.train(1)
        self.assertEqual(len(self.bpe.merges), 1)

    def test_merge_order_is_priority(self):
        self.bpe.train(3)
        # each key in merges maps to its step index
        for step, (_, idx) in enumerate(self.bpe.merges.items()):
            self.assertEqual(idx, step)

    def test_most_frequent_merged_first(self):
        # ('a','a') count=4, ('a','b')=2, ('b','_')=2
        self.bpe.train(1)
        self.assertIn(("a", "a"), self.bpe.merges)

    def test_train_stops_when_no_pairs(self):
        # single unique char — after one merge no more pairs
        path = make_jsonl(["ab"])
        bpe = BPE(path)
        os.unlink(path)
        # should not raise even if num_merge > possible merges
        bpe.train(100)
        self.assertLessEqual(len(bpe.merges), 2)

    def test_zero_merges(self):
        self.bpe.train(0)
        self.assertEqual(self.bpe.merges, {})


class TestEncode(unittest.TestCase):
    """Tests for __encode_word once implemented."""
    
    def setUp(self):
        # "ab ab c" → tokens: ["ab", "ab", "c"]
        # word_freq: {('a','b','_'): 2, ('c','_'): 1}
        # encoding: ab_ ab_ c_
        self.path = make_jsonl(["ab ab c"])
        self.bpe = BPE(self.path)

    def tearDown(self):
        os.unlink(self.path)

    def _make_trained_bpe(self, text: str, num_merge: int) -> BPE:
        path = make_jsonl([text])
        bpe = BPE(path)
        os.unlink(path)
        bpe.train(num_merge)
        return bpe

    def test_encode_known_word(self):
        bpe = self._make_trained_bpe("ab ab ab", 10)
        # after merging ('a','b') the word 'ab' should encode to ('ab_')
        result = bpe._BPE__encode_word(tuple("ab" + "_"))
        self.assertEqual(str(result[0]), "ab_")

    def test_encode_respects_merge_priority(self):
        bpe = self._make_trained_bpe("abab abab", 10)
        result = bpe._BPE__encode_word(tuple("abab" + "_"))
        self.assertIsInstance(result, tuple)
        
    def test_encode_corpus(self):
        self.bpe.train(10)
        result = self.bpe.encode(self.path) 
        self.assertEqual(result, "ab_ ab_ c_\n")


if __name__ == "__main__":
    unittest.main()
