from typing import Union, Callable
import string
import time
import tkinter as tk
import tkinter.font as font
from models import LetterState


class GuessLetter(tk.Frame):

    # instance variables
    settings: dict  # the dictionary with all the UI settings
    label: tk.Label  # the label containing the text for this frame

    def __init__(self, parent: Union[tk.Tk, tk.Frame], row: int, col: int, settings: dict) -> None:
        super().__init__(parent)

        self.settings = settings

        self['width'] = settings['ui']['guesses']['letter_box_size']
        self['height'] = settings['ui']['guesses']['letter_box_size']
        self['bg'] = settings['ui']['guesses']['initial_bg_color']

        # set bg of this frame (self) using the initial_bg_color in the settings

        self['bg'] = settings['ui']['guesses']['initial_bg_color']

        # use grid to set the location of this key to be row and column.
        # Use the padx and pady parameters to grid to provide spacing between
        # letters (both sides and top/bottom), based on the letter_padding
        # given in the settings

        self.grid(row=row, column=col, padx=settings['ui']['guesses']['letter_padding'],
                  pady=settings['ui']['guesses']['letter_padding'])

        self.grid_propagate(False)

        f = font.Font(family=settings['ui']['font_family'])

        # create the label, setting the bg to initial_bg_color and fg to
        # initial_text_color in settings. Set the font parameter to a tuple of
        # f and the letter_font_size)
        self.label = tk.Label(self, bg=settings['ui']['guesses']['initial_bg_color'], fg=settings['ui']['guesses']
                              ['initial_text_color'], font=(f, settings['ui']['guesses']['letter_font_size']))

        # don't change anything below here
        self.label.grid(row=1, column=1, sticky='ewns')

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def set_letter(self, letter: str) -> None:
        """ Set's the label's text to the letter.

        Precondition: letter is only a single character.

        Parameter:
            letter: (str) The letter to set this to.
        """
        assert len(letter) == 1, "Precondition not met!!!"
        self.label['text'] = letter

    def set_status(self, state: LetterState) -> None:
        """ Changes the background color based on the LetterState (using the
        colors defined in settings) and the text/fg color (also based on
        settings).

        Parameters:
            state (LetterState): The state used to determine the color of the background and foreground (text)
        """
        if state == LetterState.CORRECT:
            self.label['bg'] = self.settings['ui']['correct_color']
            self.label['fg'] = self.settings['ui']['guesses']['updated_text_color']
            self['bg'] = self.settings['ui']['correct_color']
        elif state == LetterState.MISPLACED:
            self.label['bg'] = self.settings['ui']['misplaced_color']
            self.label['fg'] = self.settings['ui']['guesses']['updated_text_color']
            self['bg'] = self.settings['ui']['misplaced_color']
        else:
            self.label['bg'] = self.settings['ui']['incorrect_color']
            self.label['fg'] = self.settings['ui']['guesses']['updated_text_color']
            self['bg'] = self.settings['ui']['incorrect_color']


class GuessesFrame(tk.Frame):
    """ A Tk Frame used to display the guesses that user has made. """

    # instance variables
    settings: dict  # the dictionary with all the UI settings
    # 2D list of letters (i.e. the matrix of guess letter)
    guess_letters: list[list[GuessLetter]]

    def __init__(self, parent: Union[tk.Tk, tk.Frame], settings: dict) -> None:
        super().__init__(parent)

        self.settings = settings

        self['height'] = settings['ui']['guesses']['frame_height']
        self['width'] = settings['ui']['window_width']

        self.pack(pady=(20, 0))
        self.pack_propagate(False)

        self.guess_letters = []

        # create a GuessLetter for all the guesses, adding them to
        # self.guess_letters. This should be a matrix of word size by num
        # guesses.
        for row in range(settings['num_guesses']):
            inner_list = []
            for col in range(settings['word_size']):
                inner_list.append(GuessLetter(self,
                                              row, col, settings))
            self.guess_letters.append(inner_list)

        # Center guess frames in the larger guess frame.
        self.columnconfigure(0, weight=1)
        self.columnconfigure(settings['word_size']+1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(settings['num_guesses']+1, weight=1)

    def set_letter(self, letter: str, guess_num: int, letter_index: int) -> None:
        """ Sets the guess letter at the <letter_index> in the specified <guess_num> to <letter>.

        Preconditions:
            guess_num is between 0 and num guesses
            col is between 0 and word size

        Parameters:
            row is between 0 and num guesses
            col is between 0 and word size
        """
        assert 0 <= guess_num < self.settings['num_guesses']
        assert 0 <= letter_index < self.settings['word_size']

        self.guess_letters[guess_num][letter_index].set_letter(letter)

    def show_guess_result(self, guess_num: int, results: list[LetterState]) -> None:
        """ Updates the specific guess based on the given results.

        Note that there should be a delay between the update of each letter in
        the guess; this delay time is located in self.settings.

        Preconditon: len(results) == word size

        Parameters:
            guess_num: (int) The number of the guess to update
            results: (list[LetterState]) The state of each letter in the guess.

        """
        assert len(results) == self.settings['word_size']

        for i in range(self.settings['word_size']):
            self.guess_letters[guess_num][i].set_status(results[i])
            self.update()
            time.sleep(1)


class MessageFrame(tk.Frame):
    """ A Tk Frame used to display a message to the user. """

    def __init__(self, parent, settings: dict) -> None:
        super().__init__(parent)

        self['height'] = settings['ui']['messages']['frame_height']

        self.pack(pady=20, fill=tk.X)
        self.pack_propagate(False)

        self.message_str = tk.StringVar()
        f = font.Font(family=settings['ui']['font_family'])
        message_label = tk.Label(self, textvariable=self.message_str,
                                 font=(f, settings['ui']['messages']['font_size']))
        message_label.place(relx=.5, rely=.5, anchor="center")

        self.message_timer = None
        self.set_message("It's Wordy time. Let's GO!!!")

    def set_message(self, message: str, time: int = 0):
        """ Sets the message, clearing it after the specified amount of time.

        Note that the unit of <time> will be seconds. If <time> is zero

        Precondition: time is non-negative

        Parameters:
            message: (str) The message to use
            time: (int) The length of time (in seconds) before the message will be cleared.
        """
        assert time >= 0

        if self.message_timer is not None:
            self.window.after_cancel(self.message_timer)
            self.message_timer = None

        self.message_str.set(message)

        if time > 0:
            self.message_timer = self.window.after(time * 1000,
                                                   self.clear_message)

    def clear_message(self):
        """ Clears the message. """
        self.message_str.set("")
        self.message_timer = None


class KeyboardFrame(tk.Frame):
    """ A Tk Frame used to display a keyboard to the user. """

    keyboard_buttons: dict[str, tk.Button]

    def __init__(self, parent, settings: dict) -> None:
        super().__init__(parent)

        self.settings = settings

        self['height'] = settings['ui']['keyboard']['frame_height']
        self['width'] = settings['ui']['window_width']

        # put solid border around keyboard to really make it POP!
        self['borderwidth'] = 1
        self['relief'] = 'solid'

        self.pack(fill=tk.X, ipadx=10, ipady=20)
        self.pack_propagate(False)

        self.keyboard_buttons = {}
        self.add_keyboard_buttons()

    def add_keyboard_buttons(self) -> None:
        """ Creates and places keyboard buttons. """

        # Create frames for the rows of keyboard buttons
        keyboard_button_frames = []

        for i in range(3):
            frame = tk.Frame(self)
            frame.grid(row=i+1, column=1)
            keyboard_button_frames.append(frame)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        layout = self.settings['ui']['keyboard']['key_layout']

        f = font.Font(family=self.settings['ui']['font_family'])

        # Create keyboard buttons
        for r in range(3):
            for c in range(len(layout[r])):
                if layout[r][c] == 'ENTER':
                    button = tk.Button(keyboard_button_frames[r],
                                       width=self.settings['ui']['keyboard']['key_width_long'],
                                       text=layout[r][c],
                                       fg=self.settings['ui']['keyboard']['text_color'],
                                       font=f)

                elif layout[r][c] == "BACK":
                    button = tk.Button(keyboard_button_frames[r],
                                       width=self.settings['ui']['keyboard']['key_width_long'],
                                       text=layout[r][c],
                                       fg=self.settings['ui']['keyboard']['text_color'],
                                       font=f)
                else:
                    button = tk.Button(keyboard_button_frames[r],
                                       width=self.settings['ui']['keyboard']['key_width'],
                                       text=layout[r][c],
                                       fg=self.settings['ui']['keyboard']['text_color'],
                                       font=f)

                button.grid(row=r, column=c)

                self.keyboard_buttons[layout[r][c].lower()] = button

    def set_key_colors(self, key_states: dict[str, LetterState]) -> None:
        """ Updates the colors of keys based on their states.

        Parameters:
            key_states (dict[str, LetterState]): Dictionary mapping key to its state
        """
        for letter, state in key_states.items():
            if state == LetterState.CORRECT:
                text_color = self.settings["ui"]["correct_color"]
            elif state == LetterState.INCORRECT:
                text_color = self.settings["ui"]["incorrect_color"]
            else:
                text_color = self.settings["ui"]["misplaced_color"]

            self.keyboard_buttons[letter]['fg'] = text_color

    def disable(self):
        """ Disables the keyboard by setting the state of all buttons to 'disabled'. """
        for button in self.keyboard_buttons.values():
            button['state'] = "disabled"

    def set_key_handler(self, key: str, handler: Callable[[], None]) -> None:
        """ Sets the handler for the given keyboard key.

        Precondition:
            key is a valid keyboard key (i.e. A-Z, "ENTER", or "BACK")

        Parameters:
            key: (str) The keyboard key to set the handler for.
            handler: Callable[[], None]) The handler function to call when the key is pressed.
        """
        # assert key is alphabetic, or ascii code for enter, or ascii value for backspace
        assert key.isalpha() or ord(key) == 13 or ord(key) == 8
        # set the command for the tk button in the keyboard_buttons dictionary's values based on the key
        self.keyboard_buttons[key.lower()]['command'] = handler


class WordyView:
    def __init__(self, settings):

        self.settings = settings

        # Create window and set title
        self.window = tk.Tk()
        self.window.title("Wordy")

        # Create three primary window frames: guesses, messages, and keyboard

        # assign self.guess_frame to a new GuessesFrame object
        self.guess_frame = GuessesFrame(self.window, settings)
        self.message_frame = MessageFrame(self.window, settings)
        self.keyboard_frame = KeyboardFrame(self.window, settings)

    def set_letter(self, letter: str, guess_num: int, letter_index: int):
        """ Sets the guess letter at the <letter_index> in the specified <guess_num> to <letter>.

        Preconditions:
            guess_num is between 0 and num guesses
            col is between 0 and word size

        Parameters:
            letter: (str) The letter
            guess_num: (int) The number of the guess to update
            letter_index: (int) The index in the guess that will be updated
        """
        self.guess_frame.set_letter(letter, guess_num, letter_index)

    def start_gui(self):
        """ Starts the GUI. """
        self.window.mainloop()

    def quit_program(self):
        """ Quits the program by shutting down the Tk window. """
        self.window.destroy()

    def set_key_handler(self, key: str, handler: Callable[[], None]) -> None:
        """ Sets the handler for the given keyboard key.

        Precondition:
            key is a valid keyboard key (i.e. A-Z, "ENTER", or "BACK")

        Parameters:
            key: (str) The keyboard key to set the handler for.
            handler: Callable[[], None]) The handler function to call when the key is pressed.
        """
        self.keyboard_frame.set_key_handler(key, handler)

    def create_binding(self, event_type: str, action: Callable[[tk.Event], None]):
        """ Sets the function to call when the given event type happens. """
        self.window.bind(event_type, action)

    def display_guess_result(self, guess_num: int, guess_results: list[LetterState], letter_states: dict[str, LetterState]) -> None:
        """ Updates the guess frame to show the results for the given guess number.

        Parameters:
             guess_num: (int) The number of the guess to update.
             guess_results: (list[LetterState]) The state of each letter in the guess.
             letter_states: (dict[str, LetterState]) The state of each letter in the guess.
        """
        self.guess_frame.show_guess_result(guess_num, guess_results)
        self.keyboard_frame.set_key_colors(letter_states)

    def display_message(self, msg: str) -> None:
        """ Displays the given message in the message frame.

        Parameters:
            msg: (str) The message to use.
        """
        self.message_frame.set_message(msg)

    def game_over(self) -> None:
        """ Ends the game by disabling all further keyboard input. """
        self.keyboard_frame.disable()
