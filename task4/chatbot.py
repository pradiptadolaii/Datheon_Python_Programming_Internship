"""Answer common questions for the fictional Northstar Gear shop."""

import re

FAQ = {
    "hours": (
        r"\b(?:hours?|open(?:ing)?|clos(?:e|ing)|weekends?)\b",
        "The shop is open Monday to Saturday, 10 a.m. to 6 p.m. IST.",
    ),
    "shipping": (
        r"\b(?:ship(?:ping)?|deliver(?:y|ies)?|track(?:ing)?|how long)\b",
        "Standard shipping takes 3–5 business days. The dispatch email includes a tracking link.",
    ),
    "returns": (
        r"\b(?:returns?|refunds?|exchanges?|send (?:it|them) back)\b",
        "You can return unused items within 30 days with the receipt.",
    ),
    "backpack": (
        r"\b(?:backpacks?|capacity|laptop|waterproof|water resistant)\b",
        "The Trail Backpack holds 22 litres and fits a 15-inch laptop. It is water-resistant.",
    ),
    "warranty": (
        r"\b(?:warrant(?:y|ies)|guarantee|defects?|coverage|covered)\b",
        "Northstar Gear covers manufacturing defects for one year from purchase.",
    ),
}

RULES = {topic: (re.compile(pattern), response)
         for topic, (pattern, response) in FAQ.items()}
EXIT_COMMANDS = {"bye", "exit", "quit"}
HELP = "Ask about shop hours, shipping, returns, the Trail Backpack, or warranty."
FOLLOW_UP = re.compile(r"\b(?:what about that|tell me more|more details|how does that work)\b")
DETAILS = {
    "hours": "The shop is closed on Sundays.",
    "shipping": "Transit time is counted from dispatch.",
    "returns": "Have your order number ready when contacting support about a return.",
    "backpack": "Use a separate rain cover if you expect sustained heavy rain.",
    "warranty": "Keep your receipt so support can check the purchase date.",
}


class SupportChat:
    def __init__(self):
        self.last_topics = []

    def reply(self, message):
        normalized = " ".join(re.findall(r"\w+", message.casefold()))
        if not normalized:
            return "Please enter a question. " + HELP

        # Order replies by where each intent first appears in the question.
        matches = []
        for topic, (pattern, answer) in RULES.items():
            match = pattern.search(normalized)
            if match:
                matches.append((match.start(), topic, answer))
        if matches:
            matches.sort()
            self.last_topics = [topic for _, topic, _ in matches]
            return "\n".join(answer for _, _, answer in matches)

        if FOLLOW_UP.search(normalized) and self.last_topics:
            return "\n".join(DETAILS[topic] for topic in self.last_topics)
        if normalized in {"hello", "hi", "hey", "help"}:
            return HELP
        return "I couldn't find an answer to that. " + HELP


def main():
    chat = SupportChat()
    print("Northstar Gear Support")
    print(HELP + " Type bye, exit, or quit to leave.")
    while True:
        try:
            message = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nSupport: Goodbye!")
            return
        if message.strip().casefold().rstrip("!?.").rstrip() in EXIT_COMMANDS:
            print("Support: Goodbye!")
            return
        print("Support:", chat.reply(message))


if __name__ == "__main__":
    main()
