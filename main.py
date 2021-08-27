# Standard Library Imports
import time, shutil, textwrap, math
import curses

# Local Imports
import utils

class App:
    # Layout
    size = shutil.get_terminal_size()
    margin_x = 2
    textbox_width = 40
    textbox_height = 3
    
    # App State - Store Input and other Data
    title = "Python Typer"

    text = utils.lipsum
    typed = ""

    statusbar = ""

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
        curses.init_pair(11, curses.COLOR_RED, curses.COLOR_BLACK) # Wrong Text
        curses.init_pair(40, curses.COLOR_BLACK, curses.COLOR_WHITE) # Header & Footer
        curses.init_pair(41, curses.COLOR_WHITE, curses.COLOR_WHITE) # Border

        # Main Loop
        while True:
            ### Rendering Components ###
            self.screen.clear()

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

            # Text Holder
            holder_x = (self.size.columns - self.textbox_width) // 2
            self.textBox(self.textbox_height, self.textbox_width, holder_x, 13, curses.color_pair(41))

            # Text Renderer
            self.renderText(self.textbox_height, self.textbox_width, holder_x, 13)

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
            self.typed += chr(key)
            self.statusbar = "KEY: " + chr(key)

        # If BACKSPACE is pressed, remove last character from type text
        elif key == curses.KEY_BACKSPACE:
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

        for ch_y in range(height):
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




App()
