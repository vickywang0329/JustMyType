"""
compatibility.py
Calculates a compatibility score (45-100) between two MBTI types.

Labels:
  90-100 = Excellent match, 75-89 = Good match,
  60-74  = Moderate match,  below 60 = Challenging match

This is a simplified, rule-based model for a programming project and is not
a scientifically validated measure. Each of the 4 dimensions contributes up to
25 points:
  E/I : different = 25 (energy levels balance each other), same = 15
  S/N : same      = 25 (shared way of seeing the world), different = 5
  T/F : different = 25 (complementary decision styles), same = 15
  J/P : same      = 25 (similar lifestyle, less friction), different = 10
"""

from personality import is_valid_type

# dimension index -> (points if same, points if different, reason if same, reason if different)
RULES = {
    0: (15, 25, "Both share the same social energy, which feels comfortable but can become one-sided.",
        "One is more outgoing and one more reserved, so they balance each other."),
    1: (25, 5, "They see the world the same way, so communication comes easily.",
        "One focuses on facts, the other on ideas - misunderstandings are more likely."),
    2: (15, 25, "They make decisions the same way, but may share the same blind spots.",
        "Logic and empathy complement each other in decision-making."),
    3: (25, 10, "Similar attitudes to planning reduce day-to-day friction.",
        "Planner vs. go-with-the-flow can cause tension over schedules."),
}


def calculate_compatibility(type1, type2):
    """Return (score, list_of_explanations) for two MBTI types.

    Raises ValueError if either type is invalid.
    """
    if not (is_valid_type(type1) and is_valid_type(type2)):
        raise ValueError(f"Invalid MBTI type: {type1!r} or {type2!r}")

    t1 = type1.strip().upper()
    t2 = type2.strip().upper()
    score = 0
    explanations = []
    for i in range(4):
        same_points, diff_points, same_reason, diff_reason = RULES[i]
        if t1[i] == t2[i]:
            score += same_points
            explanations.append(f"{t1[i]} & {t2[i]} (+{same_points}): {same_reason}")
        else:
            score += diff_points
            explanations.append(f"{t1[i]} & {t2[i]} (+{diff_points}): {diff_reason}")
    return score, explanations


def compatibility_label(score):
    """Turn a numeric score into a short label."""
    if score >= 90:
        return "Excellent match"
    if score >= 75:
        return "Good match"
    if score >= 60:
        return "Moderate match"
    return "Challenging match"
