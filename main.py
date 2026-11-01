"""
main.py  <-- RUN THIS FILE
JustMyType: MBTI Personality Quiz & Compatibility Analyzer
COMP9001 Final Project - I-Hsiao Wang

How to run:   python main.py
Run tests:    python -m unittest test_mbti.py -v

Only Python built-in libraries are used.
questions.txt must be in the same folder as this file.
"""

import sys

from quiz import build_tree, traverse
from question_bank import load_questions, to_dimensions, DIMENSION_ORDER
from personality import PROFILES, get_profile, is_valid_type
from compatibility import calculate_compatibility, compatibility_label
from records import RecordManager, format_record
from charts import bar, strength_bar, count_chart

MENU = """
============ JustMyType ============
1. Take the personality quiz
2. View a personality profile
3. Check compatibility between two people
4. View quiz history
5. Exit
===================================="""

SCALE = "1 = strongly (a)   2 = slightly (a)   3 = neutral   4 = slightly (b)   5 = strongly (b)"


# ---------- input helpers ----------

def get_choice(prompt, valid_options):
    """Keep asking until the user enters one of valid_options."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in valid_options:
            return answer
        print(f"  Please enter one of: {', '.join(valid_options)}")


def get_name(prompt="Enter your name: "):
    """Keep asking until a non-empty name is entered."""
    while True:
        name = input(prompt).strip()
        if name:
            return name
        print("  Name cannot be empty.")


def make_terminal_asker():
    """Return an ask(question) function that numbers the questions as it goes."""
    counter = [0]   # list so the inner function can modify it

    def ask(question):
        counter[0] += 1
        print(f"\nQ{counter[0]}. {question.text}")
        print(f"   (a) {question.option_a}")
        print(f"   (b) {question.option_b}")
        return int(get_choice("Your answer (1-5): ", ["1", "2", "3", "4", "5"]))

    return ask


def resolve_type(text, records):
    """Accept either an MBTI code or a name that exists in the records."""
    if is_valid_type(text):
        return text.strip().upper()
    found = records.latest_type_for(text)
    if found:
        print(f"  Found {text}'s latest result: {found}")
    return found


# ---------- menu actions ----------

def take_quiz(tree, records):
    name = get_name()
    print(f"\nHi {name}! Each question has two options. Answer on this scale:")
    print("  " + SCALE)
    print("If your answers in an area are close, you may get a few extra questions.")

    mbti_type, scores, asked = traverse(tree, make_terminal_asker())

    print(f"\nYour personality type is: {mbti_type}  ({sum(asked.values())} questions answered)\n")
    print(get_profile(mbti_type).display())
    print(f"\nHow strongly you lean towards each letter of {mbti_type}:")
    for (dim, letter_a, _), letter in zip(DIMENSION_ORDER, mbti_type):
        # scores store the % towards the first letter (E, S, T, J)
        pct = scores[dim] if letter == letter_a else 100 - scores[dim]
        print("  " + strength_bar(letter, pct))

    records.save(name, mbti_type, scores)
    print("\nYour result has been saved.")


def view_profile():
    code = input("Enter an MBTI type (e.g. INTJ), or 'all' to list types: ").strip()
    if code.lower() == "all":
        for profile in PROFILES.values():
            print(" ", profile)
        return
    profile = get_profile(code)
    if profile:
        print(profile.display())
    else:
        print("  That is not a valid MBTI type.")


def check_compatibility(records):
    print("Enter an MBTI type (e.g. ENFP) or the name of someone who has taken the quiz.")
    type1 = resolve_type(input("Person 1: "), records)
    type2 = resolve_type(input("Person 2: "), records)
    if type1 is None or type2 is None:
        print("  Could not find a valid type for one of the inputs.")
        return

    score, explanations = calculate_compatibility(type1, type2)
    print(f"\n{type1} + {type2}: {score}/100 - {compatibility_label(score)}")
    print(f"  {bar(score / 100, 30)} {score}%")
    for line in explanations:
        print("  -", line)
    print("(Note: this is a simplified rule-based model, just for fun.)")


def view_history(records):
    print("\na) All records   b) Search by name   c) Search by type   d) Type statistics")
    choice = get_choice("Choose (a/b/c/d): ", ["a", "b", "c", "d"])

    if choice == "a":
        results = records.load_all()
    elif choice == "b":
        results = records.find_by_name(get_name("Name to search: "))
    elif choice == "c":
        code = input("Type to search: ")
        if not is_valid_type(code):
            print("  That is not a valid MBTI type.")
            return
        results = records.find_by_type(code)
    else:
        lines = count_chart(records.type_statistics())
        if not lines:
            print("  No records yet.")
        for line in lines:
            print("  " + line)
        return

    if not results:
        print("  No matching records.")
    for record in results:
        print(" ", format_record(record))


def main():
    try:
        tree = build_tree(to_dimensions(load_questions()))
    except (FileNotFoundError, ValueError) as e:
        print(f"Could not load the question bank: {e}")
        print("Make sure questions.txt is in the same folder as main.py.")
        sys.exit(1)

    records = RecordManager()
    while True:
        print(MENU)
        choice = get_choice("Select an option (1-5): ", ["1", "2", "3", "4", "5"])
        if choice == "1":
            take_quiz(tree, records)
        elif choice == "2":
            view_profile()
        elif choice == "3":
            check_compatibility(records)
        elif choice == "4":
            view_history(records)
        else:
            print("Goodbye. See you next time!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye. See you next time!")
