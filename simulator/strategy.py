from casinobot.blackjack import hand_value


class BlackjackStrategy:
    def __init__(self, strat_table, out=None):
        self.strat_table = strat_table
        self.output = out

    def print(self, *args):
        if self.output is not None:
            self.output(*args)

    def get_strat(self, dealer, hand, force_value=False):
        dealer = self.get_blackjack_rank(dealer)
        val = str(hand_value(hand))

        if force_value:
            if val not in self.strat_table[dealer]:
                print("Max splits and no backup entry in strat table, standing!")
                print("Hand value:", val)
                print("Cards:", self.get_card_combo(hand))
                return 'S'
            return self.strat_table[dealer][val]

        thing = self.get_pair_hand(hand) or self.get_ace_hand(
            hand) or self.get_card_combo(hand)

        if thing not in self.strat_table[dealer]:
            thing = val

        if thing not in self.strat_table[dealer]:
            print("No entry in strat table, standing!")
            print("Hand value:", val)
            print("Cards:", self.get_card_combo(hand))
            return 'S'

        self.print("hand value:", val)
        self.print("hand in strat table:", thing)

        return self.strat_table[dealer][thing]

    @staticmethod
    def from_file(file, out=None):
        """
        Loads a strategy from the given `file`.

        Format is a row-column, whitespace-separated table.
        First row is a header with with dealer's visible card as column names.
        First column contains the player's card value, card combinations, ace-card combinations and pairs.
        See folder `strats/` for examples.
        """
        strat = {}
        with open(file, 'r') as f:
            header = next(f).split()
            for dealer_card in header:
                strat[dealer_card] = {}
            for line in f:
                row = line.split()
                if row:
                    own_cards = row.pop(0)
                    for i, h in enumerate(header):
                        strat[h][own_cards] = row[i]

        return BlackjackStrategy(strat, out)

    @staticmethod
    def get_blackjack_rank(rank):
        """
        Translates card rank into blackjack rank (JQK -> 10).
        """
        if rank in ('J', 'Q', 'K'):
            return '10'

        return str(rank)

    @staticmethod
    def get_pair_hand(hand):
        """
        If `hand` is a pair, returns it as combined string ("10,10"), otherwise `None`.
        """
        if len(hand.cards) != 2:
            return None

        if hand.cards[0].rank != hand.cards[1].rank:
            return None

        rank = BlackjackStrategy.get_blackjack_rank(hand.cards[0].rank)

        return rank + "," + rank

    @staticmethod
    def get_ace_hand(hand):
        """
        If `hand` is an ace and some other card, returns it as a combined string ("A,8"), otherwise `None`.
        """
        if len(hand.cards) != 2:
            return None

        if hand.cards[0].rank != 'A' and hand.cards[1].rank != 'A':
            return None

        if hand.cards[0].rank == 'A':
            return 'A,' + BlackjackStrategy.get_blackjack_rank(hand.cards[1].rank)
        else:
            return 'A,' + BlackjackStrategy.get_blackjack_rank(hand.cards[0].rank)

    @staticmethod
    def get_card_combo(hand):
        """
        Returns `hand` as a two-card combined string ("5,7"). Returns `None` if hand has more than two cards.
        """
        if len(hand.cards) != 2:
            return None

        cards = [hand.cards[0].rank, hand.cards[1].rank]
        cards.sort()

        return cards[0] + ',' + cards[1]
