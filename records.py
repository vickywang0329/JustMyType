"""
records.py
File I/O: saves quiz results to a CSV file and lets the user query history.
"""

import csv
import os
from datetime import datetime

RECORD_FILE = "quiz_records.csv"
DIMENSIONS = ["EI", "SN", "TF", "JP"]
FIELDS = ["timestamp", "name", "type"] + DIMENSIONS


class RecordManager:
    """Reads and writes quiz records in a CSV file.

    The EI / SN / TF / JP columns store the % towards the FIRST letter
    (E, S, T, J), so e.g. EI = 25 means 25% E and 75% I.
    """

    def __init__(self, filename=RECORD_FILE):
        self.filename = filename

    def save(self, name, mbti_type, scores):
        """Append one quiz result. Writes a header row if the file is new."""
        file_is_new = not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "name": name.strip(),
            "type": mbti_type,
        }
        for dim in DIMENSIONS:
            row[dim] = scores.get(dim, "")
        with open(self.filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            if file_is_new:
                writer.writeheader()
            writer.writerow(row)

    def load_all(self):
        """Return all valid records as a list of dicts. Missing file -> empty list."""
        if not os.path.exists(self.filename):
            return []
        records = []
        try:
            with open(self.filename, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    # Skip malformed rows instead of crashing
                    if row.get("name") and row.get("type"):
                        records.append(row)
        except (OSError, csv.Error) as e:
            print(f"Warning: could not read records ({e}).")
        return records

    def find_by_name(self, name):
        """Records whose name matches (case-insensitive)."""
        target = name.strip().lower()
        return [r for r in self.load_all() if r["name"].lower() == target]

    def find_by_type(self, mbti_type):
        """Records with the given MBTI type."""
        target = mbti_type.strip().upper()
        return [r for r in self.load_all() if r["type"] == target]

    def latest_type_for(self, name):
        """Most recent type for a person, or None if they have no records."""
        matches = self.find_by_name(name)
        return matches[-1]["type"] if matches else None

    def type_statistics(self):
        """Dictionary of type -> number of records, most common first."""
        counts = {}
        for r in self.load_all():
            counts[r["type"]] = counts.get(r["type"], 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def letter_strengths(record):
    """Return text like 'I 75%, N 67%, T 58%, J 83%' for the letters in the type."""
    parts = []
    for dim, letter in zip(DIMENSIONS, record["type"]):
        try:
            pct_first = int(record[dim])
        except (ValueError, TypeError, KeyError):
            parts.append(f"{letter} ?")
            continue
        pct = pct_first if letter == dim[0] else 100 - pct_first
        parts.append(f"{letter} {pct}%")
    return ", ".join(parts)


def format_record(record):
    """One-line display of a record."""
    return f"{record['timestamp']}  {record['name']:<15} {record['type']}  ({letter_strengths(record)})"
