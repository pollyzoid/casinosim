#!/usr/bin/env python

from casinobot import cards

# Global players dictionary for holding currently playing users
players = dict()
in_game = []


class Player:
    # An object for building players
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name
        self.gold = 0
        self.bet = 0
        self.hand = cards.Hand()
        self.in_game = False
        self.did_doubledown = False
        self.wins = 0
        self.nats = 0
        self.losses = 0
        self.ties = 0
        self.splits = 0
        self.surrenders = 0
        self.natlosses = 0
        self.losing_streak = 0
        self.losing_streak_max = 0
        self.winning_streak = 0
        self.winning_streak_max = 0
        self.tie_streak = 0
        self.tie_streak_max = 0
        self.surrender_streak = 0
        self.surrender_streak_max = 0
        self.hooks = None

    def __str__(self):
        string = "Player ID: %s  Name: %s  Gold: %d  Wins: %d  Losses: %d" % (
            self.uid, self.name, self.gold, self.wins, self.losses)
        if self.bet > 0:
            string += "  Bet: %d" % self.bet
        return string

    def join_game(self):
        self.in_game = True

    def leave_game(self):
        self.in_game = False

    def add_gold(self, gold):
        self.gold += int(gold)
        return True

    def remove_gold(self, gold):
        gold = int(gold)
        if gold > self.gold:
            gold = self.gold
        self.gold -= gold

    def place_bet(self, amount):
        amount = int(amount)
        if amount > self.gold:
            return 'You do not have enough gold to make that bet!'
        else:
            self.remove_gold(amount)
            self.bet += amount
            return '%s placed a bet of %d gold. They have %d gold left.' % (self.name, amount, self.gold)

    def remove_from_game(self):
        remove_from_game(self.uid)

    # Functions for winning/losing/ties
    def win_natural(self, phenny):
        self.wins += 1
        self.nats += 1
        self.losing_streak = 0
        self.tie_streak = 0
        self.surrender_streak = 0
        self.winning_streak += 1
        if self.winning_streak > self.winning_streak_max:
            self.winning_streak_max = self.winning_streak
        winnings = self.bet * 1.5
        self.add_gold(winnings + self.bet)
        if self.hooks:
            self.hooks.on_win(self, nat=True)
        self.bet = 0
        self.remove_from_game()
        phenny.write(('NOTICE', self.name + " You won " +
                      str(winnings) + " gold!"))  # NOTICE
        return "%s has a natural blackjack! They won %d gold (1.5x bet)! They now have %d gold." % (self.name, winnings, self.gold)

    def win(self, phenny, amount):
        self.wins += 1
        self.losing_streak = 0
        self.tie_streak = 0
        self.surrender_streak = 0
        self.winning_streak += 1
        if self.winning_streak > self.winning_streak_max:
            self.winning_streak_max = self.winning_streak
        self.add_gold(amount)
        winnings = amount - self.bet
        if self.hooks:
            self.hooks.on_win(self)
        self.bet = 0
        self.remove_from_game()
        phenny.write(('NOTICE', self.name + " You won " +
                      str(winnings) + " gold!"))  # NOTICE
        return "%s beat the dealer! They won %d gold! They now have %d gold." % (self.name, winnings, self.gold)

    def lose(self, phenny):
        self.losses += 1
        self.winning_streak = 0
        self.tie_streak = 0
        self.surrender_streak = 0
        self.losing_streak += 1
        if self.losing_streak > self.losing_streak_max:
            self.losing_streak_max = self.losing_streak
        if 0 in players:
            players[0].add_gold(self.bet)
        bet = self.bet
        if self.hooks:
            self.hooks.on_loss(self)
        self.bet = 0
        self.remove_from_game()
        phenny.write(('NOTICE', self.name + " You lost your bet of " +
                      str(bet) + " gold. You have " + str(self.gold) + " left."))  # NOTICE

    def tie(self, phenny):
        self.ties += 1
        self.tie_streak += 1
        if self.tie_streak > self.tie_streak_max:
            self.tie_streak_max = self.tie_streak
        self.add_gold(self.bet)
        if self.hooks:
            self.hooks.on_tie(self)
        self.bet = 0
        self.remove_from_game()
        phenny.write(
            ('NOTICE', self.name + " Your bet was returned to you."))  # NOTICE


# BASIC FUNCTIONS
def add_player(uid, nick):
    players[uid] = Player(uid, nick)


def remove_player(uid):
    del players[uid]


def name_to_uid(name):
    for uid in players:
        if players[uid].name.lower() == name.lower():
            return uid
    else:
        return None


def list_players():
    player_names = ''
    for uid in players:
        player_names += players[uid].name + ', '
    return "All Players: %s" % player_names[:-2]


def list_bets():
    all_bets = ''
    for uid in in_game:
        all_bets += players[uid].name + " - " + str(players[uid].bet) + "  "
    return "All Bets: %s " % all_bets[:-2]


# IN-GAME FUNCTIONS
def add_to_game(phenny, uid):
    uid = uid
    if uid in players.keys():
        players[uid].did_doubledown = False
        if uid in in_game:
            return "You already joined the game!"
        else:
            in_game.append(uid)
            players[uid].in_game = True
            # If player hasn't bought in yet, suggest they do
            if players[uid].gold == 0:
                phenny.write(
                    ('NOTICE', players[uid].name + " You have joined the game but not bought in yet. Use '!buy amount' to buy in."))  # NOTICE
            return "{0} joined the game.".format(players[uid].name)


def make_fake_id(uid):
    return str(uid) + "'s split" + str(players[uid].splits)


def remove_from_game(uid):
    in_game.remove(uid)
    players[uid].in_game = False


def list_in_game():
    player_names = ''
    for uid in in_game:
        player_names += players[uid].name + ', '
    return "Players In-Game: %s" % player_names[:-2]


def deal(deck, amount):
    while amount > 0:
        for uid in players:
            if players[uid].in_game == True or uid == 0:
                players[uid].hand.add_card(deck.deal_card())
        amount -= 1


if __name__ == '__main__':
    print(__doc__)
