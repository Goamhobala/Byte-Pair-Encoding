README.md

# Naive BPE

A Python tool to perform byte-pair encoding on a latin-script text data in the `.jsonl` format.

The tool expects data of the format:

```json
{text: "Maolah kako tisowanan!", ... other fields},
{text: "O Pangcah kiso?", ... other fields},
...
```

## Flags

**Example Usage:**

```python
python3 bpe.py --input_file "data/xho/train.jsonl" --output_file "test.txt" --vocab_size 1000 --cached_bpe_path="./data/xho/bpe_cached.json"
```

- `--input_file`: path to the input file
- `--output_file`: path to output the tokenised text
- `--vocab_size`: the target vocabulary size, default is 1000
- `--cache_trained_bpe`: default to true
- `--cached_bpe_path`: path to cache the trained bpe merges.
