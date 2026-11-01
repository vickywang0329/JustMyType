"""
personality.py
Defines the PersonalityType class and the personality profile database
(a dictionary mapping each 4-letter MBTI code to a PersonalityType object).
"""


class PersonalityType:
    """Stores the profile information for one MBTI personality type."""

    def __init__(self, code, nickname, description, strengths, weaknesses, careers):
        self.code = code
        self.nickname = nickname
        self.description = description
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.careers = careers

    def display(self):
        """Return a formatted, multi-line profile string."""
        line = "=" * 50
        return (
            f"{line}\n"
            f"  {self.code} - The {self.nickname}\n"
            f"{line}\n"
            f"{self.description}\n\n"
            f"Strengths : {', '.join(self.strengths)}\n"
            f"Weaknesses: {', '.join(self.weaknesses)}\n"
            f"Careers   : {', '.join(self.careers)}\n"
            f"{line}"
        )

    def __str__(self):
        return f"{self.code} ({self.nickname})"


# Raw data: code -> (nickname, description, strengths, weaknesses, careers)
_RAW_PROFILES = {
    "ISTJ": ("Inspector", "Responsible and detail-oriented. Values tradition, order and reliability.",
             ["dependable", "thorough", "practical"], ["inflexible", "reserved"],
             ["accountant", "auditor", "data analyst"]),
    "ISFJ": ("Protector", "Warm and dedicated. Quietly works hard to support the people around them.",
             ["loyal", "patient", "observant"], ["avoids conflict", "overworks"],
             ["nurse", "teacher", "HR officer"]),
    "INFJ": ("Counselor", "Insightful and idealistic. Driven by a strong sense of purpose and values.",
             ["empathetic", "visionary", "principled"], ["perfectionist", "easily burnt out"],
             ["psychologist", "writer", "UX researcher"]),
    "INTJ": ("Mastermind", "Strategic and independent. Enjoys long-term planning and complex problems.",
             ["analytical", "decisive", "self-driven"], ["overly critical", "impatient"],
             ["software architect", "scientist", "strategy consultant"]),
    "ISTP": ("Crafter", "Calm and hands-on. Loves understanding how things work by taking them apart.",
             ["resourceful", "logical", "adaptable"], ["private", "easily bored"],
             ["engineer", "mechanic", "security analyst"]),
    "ISFP": ("Composer", "Gentle and artistic. Lives in the present and expresses themselves creatively.",
             ["creative", "sensitive", "flexible"], ["dislikes planning", "self-critical"],
             ["designer", "musician", "photographer"]),
    "INFP": ("Healer", "Idealistic and caring. Guided by personal values and a rich inner world.",
             ["compassionate", "open-minded", "imaginative"], ["impractical", "takes criticism personally"],
             ["counsellor", "author", "social worker"]),
    "INTP": ("Architect", "Curious and theoretical. Enjoys exploring ideas and building logical systems.",
             ["original", "objective", "inventive"], ["absent-minded", "procrastinates"],
             ["researcher", "programmer", "mathematician"]),
    "ESTP": ("Promoter", "Energetic and action-oriented. Thrives on excitement and quick decisions.",
             ["bold", "persuasive", "practical"], ["impulsive", "impatient with theory"],
             ["salesperson", "entrepreneur", "paramedic"]),
    "ESFP": ("Performer", "Spontaneous and fun-loving. Brings energy and warmth to any room.",
             ["enthusiastic", "friendly", "observant"], ["easily distracted", "avoids long-term plans"],
             ["event planner", "actor", "tour guide"]),
    "ENFP": ("Champion", "Enthusiastic and creative. Sees possibilities everywhere and inspires others.",
             ["energetic", "curious", "people-oriented"], ["disorganised", "overcommits"],
             ["marketer", "journalist", "startup founder"]),
    "ENTP": ("Inventor", "Quick-witted and inventive. Loves debating ideas and challenging assumptions.",
             ["innovative", "adaptable", "confident"], ["argumentative", "loses interest in details"],
             ["product manager", "lawyer", "venture capitalist"]),
    "ESTJ": ("Supervisor", "Organised and decisive. Natural administrator who values structure and results.",
             ["efficient", "direct", "responsible"], ["rigid", "can seem bossy"],
             ["manager", "project lead", "financial officer"]),
    "ESFJ": ("Provider", "Sociable and caring. Works to create harmony and help others succeed.",
             ["supportive", "cooperative", "organised"], ["needs approval", "sensitive to criticism"],
             ["teacher", "customer success", "healthcare administrator"]),
    "ENFJ": ("Teacher", "Charismatic and inspiring. Motivates others and brings people together.",
             ["persuasive", "empathetic", "reliable"], ["overly idealistic", "neglects own needs"],
             ["trainer", "community leader", "HR manager"]),
    "ENTJ": ("Field Marshal", "Bold and strategic leader who organises people to reach ambitious goals.",
             ["confident", "strategic", "efficient"], ["domineering", "impatient"],
             ["executive", "investment banker", "consultant"]),
}

# The personality profile database: dictionary of code -> PersonalityType object
PROFILES = {
    code: PersonalityType(code, *data) for code, data in _RAW_PROFILES.items()
}


def is_valid_type(code):
    """Return True if code (case-insensitive) is one of the 16 MBTI types."""
    return isinstance(code, str) and code.strip().upper() in PROFILES


def get_profile(code):
    """Return the PersonalityType for code, or None if the code is invalid."""
    if not is_valid_type(code):
        return None
    return PROFILES[code.strip().upper()]
