"""Fail if a user prompt appears in both the train and validation JSONL files."""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
TRAIN_PATH = DATA_DIR / "sawyer_smeltzer_sft.jsonl"
VAL_PATH = DATA_DIR / "sawyer_smeltzer_sft_val.jsonl"


def user_prompts(path: Path) -> list[str]:
    prompts = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        users = [message["content"] for message in record["messages"] if message["role"] == "user"]
        if len(users) != 1:
            raise SystemExit(f"{path.name}:{line_number} expected exactly one user message, found {len(users)}")
        prompts.append(users[0])
    return prompts


def main() -> int:
    train = user_prompts(TRAIN_PATH)
    val = user_prompts(VAL_PATH)
    overlap = sorted(set(train) & set(val))
    if overlap:
        print("User prompts appear in both train and validation:", file=sys.stderr)
        for prompt in overlap:
            print(f"  {prompt}", file=sys.stderr)
        return 1
    print(f"No shared user prompts ({len(train)} train, {len(val)} validation).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
