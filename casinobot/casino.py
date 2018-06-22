game = False # Holds the game object
in_play = False  # Used to test if the game is in play
starting = False # Used to prevent 2 games in the rare instance 2 people try to start one at once
leaving = []  # Used to hold player ids of players who ran !left but we are waiting on confirmation from
gold = 0

def donate(phenny, force = False):
    pass