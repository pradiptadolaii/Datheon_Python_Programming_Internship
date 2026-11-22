"""Play a six-mistake word guessing game in the terminal."""

import random
import string

WORDS = ("anchor", "bamboo", "cactus", "dolphin", "garden", "lantern",
         "orchard", "puzzle", "quartz", "river", "telescope", "willow")
MAX_MISTAKES = 6


def gallows(mistakes):
    head = "O" if mistakes >= 1 else " "
    torso = "|" if mistakes >= 2 else " "
    left_arm = "/" if mistakes >= 3 else " "
    right_arm = "\\" if mistakes >= 4 else " "
    left_leg = "/" if mistakes >= 5 else " "
    right_leg = "\\" if mistakes >= 6 else " "
    return "\n".join((
        "  +---+", "  |   |", f"  |   {head}",
        f"  |  {left_arm}{torso}{right_arm}",
        f"  |  {left_leg} {right_leg}", "__|__",
    ))


def play(word):
    guesses = set()
    mistakes = 0
    print("Hangman. Guess one letter at a time. You can make six mistakes.")

    while True:
        print()
        print(gallows(mistakes))
        print("Word:", " ".join(letter if letter in guesses else "_" for letter in word))
        print("Guessed:", " ".join(sorted(guesses)) or "-")
        print("Mistakes left:", MAX_MISTAKES - mistakes)

        if set(word) <= guesses:
            print(f"You won! The word was {word}.")
            return
        if mistakes == MAX_MISTAKES:
            print(f"Game over. The word was {word}.")
            return

        guess = input("Letter: ").strip().lower()
        if len(guess) != 1 or guess not in string.ascii_lowercase:
            print("Enter one letter from A to Z.")
        elif guess in guesses:
            print("You already guessed that letter.")
        else:
            guesses.add(guess)
            if guess not in word:
                mistakes += 1


if __name__ == "__main__":
    try:
        play(random.choice(WORDS))
    except (EOFError, KeyboardInterrupt):
        print("\nGame ended.")
