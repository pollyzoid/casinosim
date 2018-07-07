# What to output when `BlackjackStats.print()` is called
OUTPUT_CONFIG = [
    #("Ending gold",     {"attr": "gold_end",    "gold": True}),
    ("Highest gold",    {"attr": "gold_max",    "gold": True}),
    ("Lowest gold",     {"attr": "gold_min",    "gold": True}),
    ("", {}),
    ("Total hands",     {"attr": "total_hands"}),
    ("", {}),
    ("Wins",            {"attr": "wins",        "percentage": True}),
    ("Losses",          {"attr": "losses",      "percentage": True}),
    ("Ties",            {"attr": "ties",        "percentage": True}),
    ("Surrenders",      {"attr": "surrenders",  "percentage": True}),
    ("", {}),
    ("NatWins",         {"attr": "nat_wins",    "percentage": True}),
    ("NatLosses",       {"attr": "nat_losses",  "percentage": True}),
    ("", {}),
    ("Win streak",      {"attr": "win_streak"}),
    ("Loss streak",     {"attr": "loss_streak"}),
    ("Tie streak",      {"attr": "tie_streak"}),
    ("Surrender streak", {"attr": "surrender_streak"}),
]


class BlackjackStats:
    gold_start = 0
    gold_target = 0
    gold_end = 0
    gold_max = 0
    gold_min = 0

    total_hands = 0
    wins = 0
    losses = 0
    ties = 0
    surrenders = 0

    nat_wins = 0
    nat_losses = 0

    win_streak = 0
    loss_streak = 0
    tie_streak = 0
    surrender_streak = 0

    def add(self, other):
        self.gold_max = max(self.gold_max, other.gold_max)
        self.gold_min = min(self.gold_min, other.gold_min)

        self.total_hands += other.total_hands
        self.wins += other.wins
        self.losses += other.losses
        self.ties += other.ties
        self.surrenders += other.surrenders
        self.nat_wins += other.nat_wins
        self.nat_losses += other.nat_losses

        self.win_streak = max(self.win_streak, other.win_streak)
        self.loss_streak = max(self.loss_streak, other.loss_streak)
        self.tie_streak = max(self.tie_streak, other.tie_streak)
        self.surrender_streak = max(
            self.surrender_streak, other.surrender_streak)

    def print(self, print_fn=print):
        for (name, stat) in OUTPUT_CONFIG:
            if name == "":
                print_fn()
                continue

            if "gold" in stat and self.gold_start == 0:
                continue

            attr = getattr(self, stat["attr"])
            if "gold" in stat:
                print_fn("{:.<16}{:.>20,}".format(name, attr), end='')
            else:
                print_fn("{:.<16}{:.>20,}".format(name, attr), end='')
            if "percentage" in stat:
                print_fn(" ({:>6.2%})".format(attr/self.total_hands), end='')
            print_fn()
