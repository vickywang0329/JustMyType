"""
question_bank.py
Loads the quiz questions from a text file (questions.txt) and validates them.

File format, one question per line:
    DIMENSION | question | option a | option b
Blank lines and lines starting with # are ignored.
"""

from quiz import Question

QUESTION_FILE = "questions.txt"
MIN_PER_DIMENSION = 3

# The order of dimensions in the decision tree, and the letters for options a / b
DIMENSION_ORDER = [("EI", "E", "I"), ("SN", "S", "N"), ("TF", "T", "F"), ("JP", "J", "P")]


def load_questions(filename=QUESTION_FILE):
    """Read the question file and return a dict: dimension -> list of Question.

    Raises FileNotFoundError if the file is missing and ValueError (with the
    line number) if a line is badly formatted or a dimension has too few questions.
    """
    valid_dims = [d[0] for d in DIMENSION_ORDER]
    bank = {dim: [] for dim in valid_dims}

    with open(filename, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 4 or not all(parts):
                raise ValueError(f"{filename} line {line_no}: expected "
                                 f"'DIMENSION | question | option a | option b'")
            dim, text, option_a, option_b = parts
            dim = dim.upper()
            if dim not in bank:
                raise ValueError(f"{filename} line {line_no}: unknown dimension '{dim}' "
                                 f"(use one of {', '.join(valid_dims)})")
            bank[dim].append(Question(dim, text, option_a, option_b))

    for dim, questions in bank.items():
        if len(questions) < MIN_PER_DIMENSION:
            raise ValueError(f"{filename}: dimension {dim} needs at least "
                             f"{MIN_PER_DIMENSION} questions, found {len(questions)}")
    return bank


def to_dimensions(bank):
    """Convert the bank into the list format build_tree() expects:
    [(dimension, letter_a, letter_b, questions), ...] in tree order."""
    return [(dim, a, b, bank[dim]) for dim, a, b in DIMENSION_ORDER]
