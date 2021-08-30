# Standard Library Imports
import time, shutil, textwrap
from datetime import datetime, timedelta
import curses

# Local Imports
import utils

class App:
    # Layout
    size = shutil.get_terminal_size()
    margin_x = 2
    textbox_width = size.columns // 2
    textbox_height = 3
    title = "Python Typer"
    
    ### App State - Store Input and other Data ###
    # Game Text
    text = utils.textGenerator()
    typed = ""
    
    # Footer
    statusbar = ""

    # Game Progress
    started = False
    ended = False
    startTime = None
    endTime = None

    # Stats
    stats = {
        'timeTaken': 0,
        'wpm': 0,
        'mistakes': 0
    }

    def __init__(self):
        # Check if terminal size is big enough
        if not (self.size.columns >= 80 and self.size.lines >= 20):
            print("=> Minimum Terminal Size : 80 x 20")
            print("=> Current Terminal Size :", self.size.columns, "x", self.size.lines)
            exit(1)

        # Initiate Curses Window through wrapper
        curses.wrapper(self.main)

    def main(self, screen: curses.window):
        # Attach Screen to Class Instance
        self.screen = screen
        curses.curs_set(0)

        # Define Color Pairs
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Title
        curses.init_pair(10, curses.COLOR_GREEN, curses.COLOR_BLACK) # Correct Text
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_RED) # Wrong Text
        curses.init_pair(40, curses.COLOR_BLACK, curses.COLOR_WHITE) # Header & Footer
        curses.init_pair(41, curses.COLOR_WHITE, curses.COLOR_WHITE) # Border

        # Main Loop
        while True:
            ### Rendering Components ###
            self.screen.clear()

            # Check if game should be ended
            if len(self.typed) == len(self.text):
                self.endGame()

            # Header & Footer
            self.screen.addstr(0, 0, '=' * self.size.columns, curses.color_pair(40))
            
            if(len(self.statusbar) > 0):
                footer = '= ' + self.statusbar + ' '
                footer += '=' * (self.size.columns - len(footer))
                self.statusbar = ''
            else:
                footer = '=' * self.size.columns

            self.screen.addstr(self.size.lines - 2, 0, footer, curses.color_pair(40))

            # ASCII Art Title
            title_ascii = utils.title_ascii.splitlines()
            for i in range(len(title_ascii)):
                self.centerText(title_ascii[i], 1 + i, curses.color_pair(1) | curses.A_BOLD)

            # Check if game has ended
            # If yes, show game stats
            if self.ended:
                self.centerText("Time Taken: " + str(self.stats['timeTaken']) + "s", 13)
                self.centerText("WPM: " + str(self.stats['wpm']), 14)
                self.centerText("Mistakes: " + str(self.stats['mistakes']), 15)
                self.screen.refresh()
                time.sleep(5)
                break

            # Text Holder
            holder_x = (self.size.columns - self.textbox_width) // 2
            self.textBox(self.textbox_height, self.textbox_width, holder_x, 13, curses.color_pair(41))

            # Text Renderer
            self.renderText(self.textbox_height, self.textbox_width, holder_x, 13)

            # Progress Bar
            progress = min(len(self.typed) / len(self.text), 1)
            progress_box = round(progress * self.textbox_width)
            progress_percent = round(progress * 100)

            self.centerText("[" + ("=" * progress_box) + (" " * (self.textbox_width - progress_box)) + "]", 15 + self.textbox_height, curses.color_pair(10))
            self.centerText(str(progress_percent) + "%", 15 + self.textbox_height)

            # Update Screen
            self.screen.refresh()

            ### Input ###
            key = self.screen.getch()
            self.input_handler(key)

    # Handles user input and stores it as App State
    def input_handler(self, key: int):
        # If ESCAPE key is pressed, quit application
        if key == 27:
            curses.endwin()
            exit(0)

        # If any other valid ASCII key is pressed, append it to typed text
        elif chr(key).isascii() and (not chr(key) == "\n"):
            if not self.handleTextInput():
                return
            self.typed += chr(key)
            self.statusbar = "KEY: " + chr(key)

        # If BACKSPACE is pressed, remove last character from type text
        elif key == curses.KEY_BACKSPACE:
            if not self.handleTextInput():
                return
            self.typed = self.typed[:-1]
            self.statusbar = "BACKSPACE"

        # Handle Resize
        elif key == curses.KEY_RESIZE:
            self.size = shutil.get_terminal_size()

    # Render Centered Text
    def centerText(self, text: str, y: int = 0, attr: int = 0):
        self.screen.addstr(y, (self.size.columns - len(text)) // 2, text, attr)

    # Render a TextBox Border
    def textBox(self, height: int, width: int, x: int, y: int, attr: int):
        self.screen.addstr(y - 1, x, "_" * (width + 1), attr) # Upper Border
        self.screen.addstr(y + height, x, "_" * (width + 1), attr) # Lower Border
        
        self.screen.addstr(y - 1, x - 2, "==", attr) # Left Border
        self.screen.addstr(y + height, x - 2, "==", attr) # Left Border
        
        self.screen.addstr(y - 1, x + width + 1, "==", attr) # Right Border
        self.screen.addstr(y + height, x + width + 1, "==", attr) # Right Border

        for i in range(height):
            self.screen.addstr(y + i, x - 2, "==", attr) # Left Border
            self.screen.addstr(y + i, x + width + 1, "==", attr) # Right Border

    # Render Game Text
    def renderText(self, height: int, width: int, x: int, y: int):
        typ_lines = textwrap.wrap(self.typed, width)
        txt_lines = textwrap.wrap(self.text, width)
        lines_typed = len(typ_lines)

        if lines_typed > 0:
            txt_lines = txt_lines[lines_typed - 1 : lines_typed + height - 1]
            typ_lines = typ_lines[-1:]
        elif len(txt_lines) - lines_typed < height:
            txt_lines = txt_lines[-height:]
            typ_lines = typ_lines[-(len(txt_lines) - lines_typed - 1):]
        else:
            txt_lines = txt_lines[:height]

        for ch_y in range(len(txt_lines)):
            for ch_x in range(len(txt_lines[ch_y])):
                # Determine Color of Text
                color = 0

                # Check if typed line has enough characters as text line
                if len(typ_lines) > ch_y :
                    if len(typ_lines[ch_y]) > ch_x:
                        # Check if character matches
                        if typ_lines[ch_y][ch_x] == txt_lines[ch_y][ch_x]:
                            color = curses.color_pair(10) # Green | Correct
                        else:
                            color = curses.color_pair(11) # Red | Incorrect
                
                # Render Character
                self.screen.addch(y + ch_y, x + ch_x, txt_lines[ch_y][ch_x], color)

    # Start Game
    def startGame(self):
        self.started = True
        self.startTime = datetime.now()
    
    # End Game
    def endGame(self):
        self.ended = True
        self.endTime = datetime.now()
        self.calcStats()

    # Calculate Stats
    def calcStats(self):
        self.stats['timeTaken'] = round((self.endTime - self.startTime).total_seconds())
        self.stats['wpm'] = int(len(self.text.split(" ")) // (self.stats['timeTaken'] / 60))

        for i in range(len(self.text)):
            if not self.text[i] == self.typed[i]:
                self.stats['mistakes'] += 1

    # Handle game input
    # If returns True, accept user input
    # If returns False, ignore user input
    def handleTextInput(self):
        # Start the game if it hasn't been started
        if not self.started:
            self.startGame()
            return True

        # Check if game is already ended
        if self.ended:
            return False

        return True

App()