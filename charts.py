"""
charts.py
Text-based bar charts for the terminal (no graphics libraries needed).
"""

FULL, EMPTY = "█", "░"


def bar(fraction, width=20):
    """Return a bar of the given width, filled according to fraction (0.0 - 1.0)."""
    fraction = max(0.0, min(1.0, fraction))
    filled = round(fraction * width)
    return FULL * filled + EMPTY * (width - filled)


LETTER_NAMES = {
    "E": "Extraversion", "I": "Introversion",
    "S": "Sensing",      "N": "Intuition",
    "T": "Thinking",     "F": "Feeling",
    "J": "Judging",      "P": "Perceiving",
}


def strength_bar(letter, pct, width=24):
    """Bar for one letter of the user's type, e.g.  I  Introversion  ████████████░░░░  83%"""
    pct = round(pct)
    name = LETTER_NAMES.get(letter, "")
    return f"{letter}  {name:<13} {bar(pct / 100, width)} {pct:>3}%"


def count_chart(counts, width=30):
    """Horizontal bar chart from a dict label -> count. Returns a list of lines."""
    if not counts:
        return []
    biggest = max(counts.values())
    total = sum(counts.values())
    lines = []
    for label, count in counts.items():
        lines.append(f"{label} {bar(count / biggest, width)} {count} ({count / total * 100:.0f}%)")
    return lines
