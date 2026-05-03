README.md

# Naive BPE

A Python tool to perform byte-pair encoding on a latin-script text data in the `.jsonl` format.

The tool expects data in this format:

```json
{text: "Maolah kako tisowanan!", ... other fields},
{text: "O Pangcah kiso?", ... other fields},
...
```

## Flags

**Example Usage:**

```python
python3 bpe.py --train_file "data/xho/train.jsonl" --output_file "test.jsonl" --vocab_size 1000 --cached_bpe_path="./data/xho/bpe_cached.json" --output_format "jsonl" --encode_file "data/xho/train.jsonl"
```

- `--train_file`: path to training file
- `--output_file`: path to output the tokenised text
- `--vocab_size`: the target vocabulary size, default is 1000
- `--cache_trained_bpe`: default to true
- `--cached_bpe_path`: path to cache the trained bpe merges.
- `--encode_file`: path to the file to be encoded
- `--output_format`: either as a `jsonl` that reflects the original format, or `txt` as a wall of text
