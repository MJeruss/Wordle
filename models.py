
import random
from enum import Enum, auto
from typing import Optional


class NotAWordError(ValueError):
    pass


class LetterState(Enum):
    INCORRECT = auto()
    MISPLACED = auto()
    CORRECT = auto()


class WordyModel:

    # instance variables
    word_size: int  # size of the word
    word_list: list[str]  # list of valid words
    word: str  # the "hidden" word

    def __init__(self, word_size, word_list_filename, preselected_word=None):
        self.word_size = word_size

        self.word_list = []
        self.set_word_list(word_list_filename)

        self.word = None
        self.set_word(preselected_word)

        self.word_letter_positions = self.letter_positions(self.word)

    def set_word_list(self, filename: str) -> None:
        """ Sets the word_list instance variable based on all the words of the
        given size (self.word_size) in the word file with name <filename>.

        Parameters:
            self (WordyModel): The object being modified.
            filename (str): name of the file containing a list of valid words.
        """
        self.word_list = []

        with open(filename, 'r') as f:
            for w in f:
                w = w.strip()
                if len(w) == self.word_size:
                    self.word_list.append(w)

        if len(self.word_list) == 0:
            raise RuntimeError(
                f"No words of length {self.word_size} found in {filename}")

    def set_word(self, preselected_word: Optional[str]) -> None:
        """ Sets the word, either to the preselected word or a random one from
        the word list if <preselected_word> is None.

        Parameters:
            preselected_word (str): The word to use for this round of the
                game, or None if a random word is to be selected.

        Raises:
            ValueError: When preselected_word isn't the proper size.
            NotAWordError: When preselected_word is not a valid word.
        """
        if preselected_word is None:
            self.word = random.choice(self.word_list)
        else:
            if len(preselected_word) != self.word_size:
                raise ValueError("preselected word isn't of the correct size")
            elif self.word not in self.word_list:
                raise NotAWordError("preselected word is not in the word list")
            else:
                self.word = preselected_word

    def check_guess(self, guess: str) -> tuple[bool, list[LetterState], dict[str, LetterState]]:
        """ Checks the given <guess> against the answer word, returning three
        things.

        (1) Whether the guess was correct
        (2) A list of LetterState to indicate for each letter in the guess
        whether it was correct, incorrect, or a mistplaced letter.
        (3) A dictionary that associates each letter in the guess with its
        state.

        Parameters:
            guess: (str) The guess to check.
        """
        # make sure guess word is actually a word
        if guess not in self.word_list:
            raise NotAWordError
        # initialize an empty list
        letter_state_list = []
        # initialize an empty dictionary
        letter_state_dict = {}
        # check letters and append to list/assign to dictionary
        for i in range(len(guess)):
            if guess[i] == self.word[i]:
                letter_state_list.append(LetterState.CORRECT)
            elif guess[i] in self.word:
                letter_state_list.append(LetterState.MISPLACED)
            else:
                letter_state_list.append(LetterState.INCORRECT)
            letter_state_dict[guess[i]] = letter_state_list[i]
        # return appropriate tuples
        if guess == self.word:
            return True, letter_state_list, letter_state_dict
        else:
            return False, letter_state_list, letter_state_dict

    def letter_positions(self, word: str) -> dict[str, list[int]]:
        """ Returns a mapping between letters and the indexes at which the
        letter appears in the word.

        Parameters:
            word: (str) the word.

        Returns:
            (dict[str, list[int]]) Dictionary with each character's position.
        """
        letter_positions = {}
        for i in range(len(word)):
            letter = word[i]
            letter_positions.setdefault(letter, []).append(i)
        return letter_positions
