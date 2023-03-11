import sys

import curses
import time

from data import *

"""
A game where the user can give problems and answers.

The game is a challenging geometry dash clone where the user must answer questions if they fall off the platform.
If they get the question wrong they lose a life and if they run out of lives they lose the game.

If they reach the end of the level they have to answer a question to progress. If they fail then they are sent back to the start.
"""
HEIGHT = 50
WIDTH = 100


class Player:
    def __init__(self):
        self.lives = 3
        self.score = 0
        self.level = 0
        self.x = 0
        self.y = 0
        self.x_velocity = 0
        self.y_velocity = 0
        self.gravity = -0.05
        self.jump_velocity = 0.7

    def jump(self):
        if self.y == 0:
            self.y_velocity = self.jump_velocity

    def update(self):
        if self.y <= 0:
            self.y = 0
            if self.y_velocity < 0:
                self.y_velocity = 0
            self.y += self.y_velocity
        else:
            self.y_velocity += self.gravity
            self.y += self.y_velocity
        self.x += self.x_velocity

    def reset(self):
        self.lives = 3
        self.score = 0
        self.level = 0
        self.x = 0
        self.y = 0
        self.x_velocity = 0
        self.y_velocity = 0
        self.gravity = 0.1
        self.jump_velocity = 0.5

    def __str__(self):
        return f"Player lives: {self.lives}, score: {self.score}, level: {self.level}, x: {self.x}, y: {self.y}, x_velocity: {self.x_velocity}, y_velocity: {self.y_velocity}, gravity: {self.gravity}, jump_velocity: {self.jump_velocity}"

    def __repr__(self):
        return f"Player lives: {self.lives}, score: {self.score}, level: {self.level}, x: {self.x}, y: {self.y}, x_velocity: {self.x_velocity}, y_velocity: {self.y_velocity}, gravity: {self.gravity}, jump_velocity: {self.jump_velocity}"


class Spike:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def update(self, difficulty: int = 2):
        self.x -= 0.1 * difficulty

    def collison_check(self, player: Player):
        if int(self.x) == 0 and int(player.y) == int(self.y):
            return True

    def __str__(self):
        return f"Spike x: {self.x}, y: {self.y}"

    def __repr__(self):
        return f"Spike x: {self.x}, y: {self.y}"


class Spikes:
    def __init__(self):
        self.spikes = []

    def add_spike(self, spike):
        self.spikes.append(spike)

    def remove_spike(self, spike):
        self.spikes.remove(spike)

    def get_spikes(self):
        return self.spikes

    def update(self, difficulty: int = 2):
        for spike in self.spikes:
            spike.update(difficulty)
            if int(spike.x) < 0:
                self.remove_spike(spike)

    def __iter__(self):
        return iter(self.spikes)


class Game:
    def __init__(self, database: Database):
        self.player = Player()
        self.spikes = Spikes()
        self.problems = database
        self.current_problem = Question("null", ["null"], 0)

        self.screen = curses.initscr()

        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.screen.nodelay(True)
        curses.curs_set(0)

        self.screen_height = curses.LINES - 1
        self.screen_width = curses.COLS - 1

    def get_new_problem(self):
        problem = self.problems.get_random_problem()
        if problem is None:
            return False
        self.current_problem = problem
        return True

    def ask_question(self):
        self.spikes.spikes = []
        self.get_new_problem()
        self.screen.clear()

        answer = ''
        while True:
            time.sleep(0.1)
            self.screen.clear()
            self.screen.addstr(0, 0, self.current_problem.question)
            self.screen.addstr(2, 0, "Answer: " + answer)
            self.screen.refresh()
            key = self.screen.getch()
            if key == curses.KEY_BACKSPACE or key == curses.KEY_DC or key == curses.KEY_DL or key == 127:
                answer = answer[:-1]
            elif key == curses.KEY_ENTER or key in [10, 13]:
                break
            elif 32 <= key <= 126:
                answer += chr(key)
        if answer.strip().lower() in self.current_problem.answer:
            self.screen.clear()
            self.screen.addstr(0, 0, "Correct!")
            self.screen.refresh()
            time.sleep(2)
            return True
        else:
            self.screen.clear()
            self.screen.addstr(0, 0, "Incorrect!" + " The correct answer was " + self.current_problem.answer[0])
            self.screen.refresh()
            time.sleep(2)
            self.player.lives -= 1
            return False

    def gen_spike(self):
        """
        Generate a spike at a random x and y position.
        """
        x: int = int(self.screen_width - 1)
        y: int = int(random.randint(0, 1))
        self.spikes.add_spike(Spike(x, y))

    def render(self):
        """
        Render a frame of the game to the screen using ascii art and curses.
        """
        self.screen.clear()

        self.screen.addstr(0, 0, "Lives: " + str(self.player.lives))
        # render the player at the bottom of the screen unless they are jumping
        self.screen.addstr(int(self.screen_height - self.player.y), int(self.player.x), "O")
        # render the spikes
        for spike in self.spikes:
            self.screen.addstr(int(self.screen_height - spike.y), int(spike.x), "X")

    def start_game(self):
        """
        Start the game loop.
        """

        clock = 0
        difficulty = 2
        while True:
            # get the current time
            start_time = time.time()

            # ramp up the difficulty
            if clock % 2000 == 0 and difficulty < 10:
                difficulty += 1

            # get the current key pressed
            key = self.screen.getch()

            # if the key is q then quit the game
            if key == ord("q"):
                break

            # if the key is space then jump
            if key == ord(" "):
                self.player.jump()

            # if the key is r then reset the game
            if key == ord("r"):
                self.player.reset()

            # if the key is a then ask the user a question
            if key == ord("a"):
                self.ask_question()

            # randomly generate a spike
            if random.randint(0, int(10000 / difficulty * 0.1)) == 0:
                self.gen_spike()

            # update the player
            self.player.update()

            # update the spikes
            self.spikes.update(difficulty)

            # check for collisions
            for spike in self.spikes:
                if spike.collison_check(self.player):
                    self.ask_question()

            # check if the player is dead
            if self.player.lives <= 0:
                break

            # render the game
            self.render()

            # refresh the screen
            self.screen.refresh()

            # get the time taken to render the frame
            frame_time = time.time() - start_time

            # add to the clock
            clock += 1

            # wait for the remainder of the frame
            if frame_time < 0.01:
                time.sleep(0.01 - frame_time)
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()


def intro():
    print("Welcome to the game!")
    print("Press space to jump")
    print("Press q to quit")
    print("Press r to reset")
    print("Press a to ask a question")
    print("Press enter to continue")
    input()


def get_problems():
    problems = Database()
    print("csv file format: question, answer")
    print("You can have multiple right answers by separating them with a semicolon")
    print("Example: What is the capital of the United States?, Washington;Washington D.C.;Washington DC;DC;D.C.")
    user_problems = input("Enter the path to the csv file: ")
    problems.read_csv(user_problems)
    return problems


if __name__ == "__main__":
    problems = get_problems()
    intro()

    game = Game(problems)

    try:
        game.start_game()
    except KeyboardInterrupt:
        game.screen.clear()
        curses.nocbreak()
        game.screen.keypad(False)
        curses.echo()
        curses.endwin()
        print("Thanks for playing!")
        sys.exit(0)
    except Exception as e:
        game.screen.clear()
        curses.nocbreak()
        game.screen.keypad(False)
        curses.echo()
        curses.endwin()
        print("An error has occured. Thanks for playing!")
        print(e)
        sys.exit(0)
