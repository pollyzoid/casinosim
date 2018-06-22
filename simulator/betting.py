class BettingSystem:
    def __init__(self):
        pass

    @staticmethod
    def parse_options(options):
        opts = {}
        for pairs in options.strip().split(','):
            kv = pairs.split('=')
            if len(kv) > 1:
                opts[kv[0]] = kv[1]
            elif len(kv) > 0:
                opts[kv[0]] = True

        return opts

    @staticmethod
    def from_options(options):
        return BettingSystem()

    def set_player(self, pl):
        self.player = pl

    def on_win(self, hands):
        pass

    def on_loss(self, hands):
        pass

    def on_tie(self):
        pass

    def get_next_bet(self):
        return 0


class NoBetting(BettingSystem):
    pass


class SimpleBetting(BettingSystem):
    def __init__(self, bet):
        BettingSystem.__init__(self)
        self.bet = bet

    @staticmethod
    def from_options(options):
        opts = BettingSystem.parse_options(options)
        if 'bet' not in opts:
            raise RuntimeError("SimpleBetting requires 'bet' option")
        return Martingale(int(opts["bet"]))

    def get_next_bet(self):
        return self.bet


class Martingale(BettingSystem):
    def __init__(self, starting):
        BettingSystem.__init__(self)

        self.starting_bet = starting
        self.next_bet = starting

    @staticmethod
    def from_options(options):
        opts = BettingSystem.parse_options(options)
        if 'starting-bet' not in opts:
            raise RuntimeError("Martingale requires 'starting-bet' option")
        return Martingale(int(opts["starting-bet"]))

    def reset(self):
        self.next_bet = self.starting_bet

    def on_win(self, hands):
        self.next_bet = self.starting_bet

    # The goal in Martingale is to recoup any losses and profit by the starting bet
    # after a string of losses. We need to count splits and doubledowns as additional wins/losses to
    # bet accurately.
    # For example, a hand is split twice into three hands. One of those loses a doubledown, one ties and one wins.
    # To win back the lost gold, we need to count the +-s from wins/losses: -2 from double loss, 0 from tie and
    # +1 from win, for a total of -1. Values <0 are losses, so `on_loss` is called with `hands=1`.
    def on_loss(self, hands):
        #print("on_loss", hands, self.next_bet)
        self.next_bet *= (1 + hands)

    def on_tie(self):
        pass

    def get_next_bet(self):
        return self.next_bet


class FlowPlayBetting(BettingSystem):
    def __init__(self, gold, stacks, levels):
        pass
