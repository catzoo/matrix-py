import random
import blessed

# configuration / constant values
max_trails = 10
max_trail_length = 50
color_enabled = True

white_rate = 100
fade_rate = 50

chars = (33, 126)  # used to grab a random character with chr()


class Trail:
    def __init__(self, term: blessed.Terminal, x, y):
        self.characters = [  # Keep track of characters in the trail
            # {
            #     "char": 'c',
            #     "y": 5,
            #     "fade": None or 255,
            #     "white": None or 255,
            #     "time": None or 0
            # }
        ]
        self.term = term
        self.x = x
        self.starting_y = y

    def _print_char(self, char):
        """
        This is used to print a character. Depending on the character, it will also change the color
        :param char: dict - has the fields: {"char", "y", "fade", "white", "time"}
        :return:
        """
        if char["white"]:
            rgb = (char["white"], 255, char["white"])
        elif char["fade"]:
            rgb = (0, char["fade"], 0)
        else:
            rgb = (0, 255, 0)
        print(self.term.move_xy(self.x, char["y"]) + self.term.color_rgb(*rgb) + char["char"])

    def _add(self):
        """
        Adds a character to the trail
        """
        y = None
        if len(self.characters) == 0:
            y = self.starting_y
        else:
            char = self.characters[len(self.characters) - 1]
            if char["fade"] is None:
                y = char["y"]
                y += 1

        if y and y < self.term.height - 2:
            char = {
                "char": chr(random.randint(*chars)),  # grabbing random character
                "y": y,
                "fade": None,
                "white": 255,
                "time": None
            }
            self.characters.append(char)
            self._print_char(char)

    def _end(self):
        """
        Checks the timing on the end character.
        Also adds timing by 1 every time its called (or updated)

        Basically, this is used to start fading the characters if its reached the max_trail_length
        """
        for k, char in enumerate(self.characters):
            if char["fade"] is None:
                if char["time"] is None:
                    # Time doesn't exist. Need to add it
                    char["time"] = 0
                else:
                    if char["time"] > max_trail_length:
                        # Start fading the character (self._update_colors helps fade it)
                        char["fade"] = random.randint(100, 255)
                        if k + 1 != len(self.characters):
                            # Add time to the next character
                            self.characters[k + 1]["time"] = max_trail_length + 1
                    else:
                        char["time"] += 1
                # Found the end character. Don't need to check the others
                break

    def _update_colors(self):
        """
        Goes through each character checking if it has white or fade

        If its fade, it will start fading the character until its disappeared
        If its white, it will have the white -> green until white is fully gone

        This also removes any characters that are fully disappeared
        """
        for k, char in enumerate(self.characters):
            if color_enabled:
                # TODO: Combine these. They do the same thing only with different values / names
                if char["white"]:
                    char["white"] -= white_rate
                    if char["white"] <= 0:
                        # Its not white anymore
                        char["white"] = None
                    self._print_char(char)

                elif char["fade"]:
                    char["fade"] -= fade_rate
                    if char["fade"] <= 0:
                        # Removing the character
                        char["char"] = " "
                        char["fade"] = 0
                        self.characters.pop(k)
                    self._print_char(char)
            else:
                if char["fade"]:
                    # No colors, so just make the character disappear if its fading
                    char["char"] = " "
                    char["fade"] = 0
                    self.characters.pop(k)
                    self._print_char(char)

    def is_empty(self):
        """
        Check if the trail is empty.

        :return: True if its empty, False if its not.
        """
        return len(self.characters) == 0

    def update(self):
        """
        Send a update the trail.

        This basically -
            - adds a new character (if its not at the end)
            - fades the end characters, if its time.
            - update the colors of white / fading characters

        :return: if the trail is empty or not
        """
        self._add()
        self._end()
        self._update_colors()

        return self.is_empty()


class Positions:
    """
    This helps group up all the trails and update them.
    Also helps with adding new trails.
    """
    def __init__(self, term):
        self.positions = {
            # starting_x: []
            # List of trails
            # position, current fade
        }
        self.term = term

    def update(self):
        """
        This updates all the trails and manages self.positions by adding new trails or removing old ones.
        """
        if len(self.positions) < max_trails:
            # Basically, this adds a new trail by chance
            # More trails there are, lower chance of adding a new trail
            percent = 100 - ((len(self.positions) / (max_trails + 1)) * 100)
            chance = random.randint(0, 100)

            x = None
            if chance <= percent:
                for _ in range(3):
                    # Making sure its not being used by another trail
                    x = random.randint(0, self.term.width)
                    if x in self.positions:
                        x = None
                    else:
                        break
            if x:
                # Found a valid x position, entering it
                # TODO: Fix bug when the terminal screen is too small
                height = int(self.term.height - (self.term.height * 0.5))
                y = random.randint(0, height)
                self.positions[x] = Trail(self.term, x, y)

        remove_pos = []
        for k, pos in self.positions.items():
            if pos.update():
                remove_pos.append(k)

        # Removing anything that is empty. Doing this after the for loop so it doesn't error / get confused
        for k in remove_pos:
            del self.positions[k]

    def clear(self):
        """Removes all the trails"""
        self.positions = {}


if __name__ == "__main__":
    term = blessed.Terminal()
    # Grabbing the current height and width. Mainly to keep track of resizing.
    # There is a signal that helps with window resizing, but windows does not support that. So, just manually checking
    # every update to see if there is a resize
    cur_height, cur_width = term.height, term.width

    with term.hidden_cursor():
        with term.cbreak():
            # Clearing the screen
            print(term.home() + term.on_black + term.clear())
            # Creating the Position
            pos = Positions(term)

            while term.inkey(timeout=0.1).lower() != 'q':
                # Sending a update to position / trails
                pos.update()
                # Checking for screen resize
                if cur_width != term.width or cur_height != term.height:
                    # Screen has been resized. Need to clear everything. Basically, restart
                    pos.clear()
                    print(term.clear() + term.on_black)
                    cur_height, cur_width = term.height, term.width
