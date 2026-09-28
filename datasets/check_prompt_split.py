"""Fail if train and validation user prompts overlap, or if an assistant answer is not paired once in each file."""

import json
import sys
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
TRAIN_PATH = DATA_DIR / "sawyer_smeltzer_sft.jsonl"
VAL_PATH = DATA_DIR / "sawyer_smeltzer_sft_val.jsonl"


def load_messages(path: Path) -> tuple[list[str], list[str]]:
    prompts = []
    answers = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        users = [message["content"] for message in record["messages"] if message["role"] == "user"]
        assistants = [message["content"] for message in record["messages"] if message["role"] == "assistant"]
        if len(users) != 1 or len(assistants) != 1:
            raise SystemExit(
                f"{path.name}:{line_number} expected one user and one assistant message, "
                f"found {len(users)} user and {len(assistants)} assistant"
            )
        prompts.append(users[0])
        answers.append(assistants[0])
    return prompts, answers


def main() -> int:
    train_prompts, train_answers = load_messages(TRAIN_PATH)
    val_prompts, val_answers = load_messages(VAL_PATH)
    failed = False

    overlap = sorted(set(train_prompts) & set(val_prompts))
    if overlap:
        failed = True
        print("User prompts appear in both train and validation:", file=sys.stderr)
        for prompt in overlap:
            print(f"  {prompt}", file=sys.stderr)

    train_counts = Counter(train_answers)
    val_counts = Counter(val_answers)
    answers = sorted(set(train_counts) | set(val_counts))
    for answer in answers:
        train_count = train_counts[answer]
        val_count = val_counts[answer]
        if train_count == 1 and val_count == 1:
            continue
        failed = True
        print(
            f"Assistant answer must appear once in train and once in validation "
            f"(train {train_count}, validation {val_count}): {answer}",
            file=sys.stderr,
        )

    if failed:
        return 1
    print(
        f"No shared user prompts, and each of {len(answers)} assistant answers "
        f"appears once in train and once in validation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
