"""
quiz.py
The decision-tree quiz. The tree is BUILT recursively and TRAVERSED recursively.

Tree structure (depth 4, 16 leaves):
    level 0 node decides E / I
    level 1 nodes decide S / N
    level 2 nodes decide T / F
    level 3 nodes decide J / P
    level 4 = leaf nodes, each holding one of the 16 type codes.

At each internal node the user answers questions about that dimension on a
1-5 scale (1 = strongly option a, 5 = strongly option b). Questions are drawn
at random from that dimension's pool. If the result is too close to call,
the node keeps asking extra questions (recursively) until it is clear,
the pool runs out, or the maximum is reached.
"""

import random

INITIAL_QUESTIONS = 3     # questions asked at every node
MAX_QUESTIONS = 7         # upper limit per node, so the quiz always ends
CLOSE_LOW, CLOSE_HIGH = 40, 60   # a result in this % range is "too close to call"

# 1-5 answer -> how much it supports option a (the first letter)
LIKERT_TO_A = {1: 1.0, 2: 0.75, 3: 0.5, 4: 0.25, 5: 0.0}


class Question:
    """One quiz question. Option a leans to the first letter, option b to the second."""

    def __init__(self, dimension, text, option_a, option_b):
        self.dimension = dimension
        self.text = text
        self.option_a = option_a
        self.option_b = option_b


class DecisionNode:
    """A node in the decision tree. Leaf nodes have a result (e.g. 'INTJ')."""

    def __init__(self, dimension=None, letters=None, questions=None, result=None):
        self.dimension = dimension      # e.g. "EI"
        self.letters = letters          # e.g. ("E", "I")
        self.questions = questions or []
        self.left = None                # child for the first letter
        self.right = None               # child for the second letter
        self.result = result            # only set for leaf nodes

    def is_leaf(self):
        return self.result is not None


def build_tree(dimensions, index=0, prefix=""):
    """Recursively build the decision tree.

    dimensions: [(dimension, letter_a, letter_b, questions), ...]
    Base case: all dimensions used -> return a leaf holding the type code.
    Recursive case: create a node for dimensions[index] and build both subtrees.
    """
    if index == len(dimensions):
        return DecisionNode(result=prefix)

    dimension, letter_a, letter_b, questions = dimensions[index]
    node = DecisionNode(dimension, (letter_a, letter_b), questions)
    node.left = build_tree(dimensions, index + 1, prefix + letter_a)
    node.right = build_tree(dimensions, index + 1, prefix + letter_b)
    return node


def percent_first(answers):
    """Percentage (0-100) of support for the first letter, from 1-5 answers."""
    if not answers:
        return 50.0
    return sum(LIKERT_TO_A[a] for a in answers) / len(answers) * 100


def ask_until_clear(pool, ask, answers):
    """Recursively ask extra questions while the result is too close to call.

    Base cases: the result is clear, the pool is empty, or MAX_QUESTIONS reached.
    Recursive case: ask one more question, then check again.
    """
    pct = percent_first(answers)
    too_close = CLOSE_LOW <= pct <= CLOSE_HIGH
    if not too_close or not pool or len(answers) >= MAX_QUESTIONS:
        return answers
    answers.append(ask(pool.pop()))
    return ask_until_clear(pool, ask, answers)


def break_tie(answers):
    """Exact 50% tie: follow the most recent non-neutral answer (default: option a)."""
    for answer in reversed(answers):
        if answer != 3:
            return answer < 3
    return True


def traverse(node, ask, rng=random, scores=None, asked=None):
    """Recursively walk from node down to a leaf.

    ask: a function that takes a Question and returns an int from 1 to 5.
         (The terminal version asks a real user; tests pass in fake answers.)
    rng: random number generator used to pick questions (tests pass a seeded one).
    Returns (type_code, scores, asked):
        scores: dimension -> % towards the FIRST letter, e.g. {"EI": 75, ...}
        asked : dimension -> number of questions asked
    """
    if scores is None:
        scores, asked = {}, {}

    # Base case: reached a leaf
    if node.is_leaf():
        return node.result, scores, asked

    # Shuffle a copy of this node's questions and ask the first few
    pool = rng.sample(node.questions, len(node.questions))
    first_round = min(INITIAL_QUESTIONS, len(pool))
    answers = [ask(pool.pop()) for _ in range(first_round)]
    answers = ask_until_clear(pool, ask, answers)

    pct = percent_first(answers)
    if pct == 50:
        go_left = break_tie(answers)
    else:
        go_left = pct > 50

    scores[node.dimension] = round(pct)
    asked[node.dimension] = len(answers)
    next_node = node.left if go_left else node.right

    # Recursive case: continue down the chosen branch
    return traverse(next_node, ask, rng, scores, asked)


def count_leaves(node):
    """Recursively count leaf nodes (should be 16)."""
    if node.is_leaf():
        return 1
    return count_leaves(node.left) + count_leaves(node.right)


def collect_results(node):
    """Recursively collect every leaf's type code."""
    if node.is_leaf():
        return [node.result]
    return collect_results(node.left) + collect_results(node.right)


def tree_depth(node):
    """Recursively compute the depth of the tree (number of decisions to a leaf)."""
    if node.is_leaf():
        return 0
    return 1 + max(tree_depth(node.left), tree_depth(node.right))
