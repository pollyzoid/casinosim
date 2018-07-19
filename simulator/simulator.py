import random
import time

from casinobot import blackjack, player
from simulator import betting, stats, strategy


class Phenny:
    """
    Mock of the IRC bot Phenny's interface
    """

    def __init__(self, out):
        self.print = out

    def say(self, msg):
        """
        Send a message to the "channel".
        """
        self.print("Phenny:", msg)
        pass

    def write(self, msg):
        """
        Send a raw(-er) IRC message, e.g. a NOTICE to a specific user.
        """
        self.print("Phenny:", msg)
        pass


class BlackjackHooks:
    """
    Contains callbacks from CasinoBot, to interface with our strategy and
    betting systems.

    Hand results and doubledowns are tracked in order to accurately pick an
    action on multi-hand rounds. E.g. splitting twice to three hands, with one doubledown
    loss (-2), one normal win (+1) and one tie (0) will be handled as one normal loss (-1).
    """

    def __init__(self, strat, betting, out=None):
        self.strat = strat
        self.betting = betting
        self.end = False
        self.end_reason = 'N/A'
        self.output = out
        self.anti_fallacy = False
        self.af_trigger = False
        self.positive_prog = False

        self.reset_results()

    def print(self, *args):
        if self.output is not None:
            self.output(*args)

    def set_positive_prog(self, enable):
        self.positive_prog = enable

    def set_anti_fallacy(self, enable):
        """
        Enable or disable anti-fallacy strat. After a loss, it bets zero until a win, then
        continues normal betting until the next loss, rinse and repeat.
        """
        self.anti_fallacy = enable

    def on_init(self, bj):
        """
        Called when the game is initialized.
        """
        self.print("on_init")

    def on_begin_game(self, bj):
        """
        Called when the game starts and bets can be placed.
        """
        self.print("on_begin_game")

        bet = self.betting.get_next_bet()
        pl = player.players[1]

        if bet == 0:
            self.end_reason = "Infinite loop: zero gold bets."
            self.end = True

        if self.af_trigger:
            bet = 0

        self.print("Betting:", bet)

        if self.betting.end_reason is not None:
            self.end_reason = self.betting.end_reason
            self.end = True
            return

        if pl.gold < bet:
            self.end_reason = "Ran out of gold."
            self.end = True
        else:
            self.print("Phenny:", pl.place_bet(bet))

    def reset_results(self):
        """
        Reset hand results.
        """
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.surrenders = 0

    def on_win(self, pl, nat=False):
        """
        Called when a hand is won.
        """
        if pl.did_doubledown:
            self.wins += 1
        self.wins += 1

    def on_loss(self, pl, surrender=False):
        """
        Called when a hand is lost.
        """
        if pl.did_doubledown:
            self.losses += 1
        self.losses += 1
        if surrender:
            self.surrenders += 1

    def on_tie(self, pl):
        """
        Called when a hand is tied.
        """
        self.ties += 1

    def on_start_turn(self, bj, uid):
        """
        Called when a player's turn starts and an action can be made.
        """
        pid = player.players[uid].uid
        self.print("on_start_turn", uid, pid)
        self.choose_action(bj, uid)

    def on_hit(self, bj, uid):
        """
        Called after hitting and an action can be made.
        """
        self.print("on_hit")
        self.choose_action(bj, uid)

    def on_game_over(self, bj):
        """
        Called when the game is over and all cards revealed.
        """
        self.print("on_game_over")
        self.print("dealer:", player.players[0].hand)
        res = self.wins - self.losses
        if self.positive_prog:
            res = -res
        self.print("res:", res)
        if res < 0:
            self.betting.on_loss(abs(res))
            if self.anti_fallacy:
                self.af_trigger = True
        elif res > 0 and not self.af_trigger:
            self.betting.on_win(res)
        elif res > 0:
            self.af_trigger = False
        else:
            self.betting.on_tie()
        self.reset_results()

    def choose_action(self, bj, uid):
        """
        Uses the dealer's visible card and own hand to pick an action from
        the selected strategy, and translates different actions to CasinoBot calls.
        """
        self.print("choose_action", uid)
        pl = player.players[player.players[uid].uid]
        bet = player.players[uid].bet
        pid = player.players[uid].uid
        hand = player.players[uid].hand
        dealer = player.players[0].hand.cards[1].rank

        st = self.strat.get_strat(dealer, hand)

        # If we're already at maximum splits (or splitting is not allowed for other reasons),
        # pick a new strategy using the card value total instead of pairs.
        if st == 'P' and (not bj.accept_split or not self.betting.can_double()):
            st = self.strat.get_strat(dealer, hand, True)

        self.print("Dealer:", bj.show_dealers_hand())
        self.print("Hand:", hand)
        self.print("Strat:", st)
        if st == 'H':
            bj.hit(pid)
        elif st == 'S':
            bj.stand(pid)
        elif st == 'P':
            if pl.gold < bet:
                print("Not enough gold to split")
            if not bj.accept_split:
                raise RuntimeError("Unable to split for some reason")
            bj.split(pid)
        elif st == 'D' or st == 'Dh':
            if bj.accept_doubledown and self.betting.can_double():
                if bet > pl.gold:
                    print("Not enough gold to doubledown")
                bj.doubledown(pid)
            else:
                bj.hit(pid)
        elif st == 'R' or st == 'Rh':
            if bj.accept_surrender:
                bj.surrender(pid)
            else:
                bj.hit(pid)
        elif st == 'Rs':
            if bj.accept_surrender:
                bj.surrender(pid)
            else:
                bj.stand(pid)
        elif st == 'Ds':
            if bj.accept_doubledown and self.betting.can_double():
                bj.doubledown(pid)
            else:
                bj.stand(pid)
        elif st == 'H*':
            if len(hand.cards) > 2:
                bj.stand(pid)
            else:
                bj.hit(pid)
        elif st == '?':
            actions = [bj.stand, bj.hit]
            if bj.accept_doubledown and self.betting.can_double():
                actions.append(bj.doubledown)
            if bj.accept_split and self.betting.can_double():
                actions.append(bj.split)
            if bj.accept_surrender:
                actions.append(bj.surrender)
            random.choice(actions)(pid)
        else:
            raise RuntimeError("missing strategy '{0}'".format(st))


class BlackjackSimulator:
    name = 'Sim'

    def __init__(self, strat, bet_system, out=None):
        self.phenny = Phenny(self.print)
        self.strat = strat
        self.bet_system = bet_system
        self.output = out

        self.starting_gold = 0
        self.target_gold = 0
        self.rounds = 0
        self.anti_fallacy = False
        self.positive_prog = False

        self.reset()

    def reset(self):
        if 1 in player.players:
            player.remove_player(1)
        player.add_player(1, self.name)
        self.player = player.players[1]
        self.hooks = BlackjackHooks(self.strat, self.bet_system, self.output)
        self.hooks.set_anti_fallacy(self.anti_fallacy)
        self.hooks.set_positive_prog(self.positive_prog)
        self.player.hooks = self.hooks
        self.stats = stats.BlackjackStats()
        self.reset_gold()
        self.bet_system.set_player(self.player)
        self.bet_system.reset()

    def reset_gold(self):
        self.player.gold = self.starting_gold
        self.stats.gold_start = self.starting_gold
        self.stats.gold_max = self.starting_gold
        self.stats.gold_min = self.starting_gold
        self.bet_system.set_starting_gold(self.starting_gold)

    def set_positive_prog(self, enable):
        self.positive_prog = enable

    def set_anti_fallacy(self, enable):
        self.anti_fallacy = enable
        self.hooks.set_anti_fallacy(enable)

    def set_starting_gold(self, gold):
        self.starting_gold = gold
        self.reset_gold()

    def set_target_gold(self, target):
        self.target_gold = target

    def print(self, *args):
        if self.output is not None:
            self.output(*args)

    def run(self, rounds):
        end_reason = "N/A"

        curr_round = 0
        while True:
            bj = blackjack.Game(self.phenny, 1, self.name, self.hooks)
            del bj
            curr_round += 1
            if rounds > 0 and curr_round >= rounds:
                end_reason = "Finished rounds."
                break
            if self.starting_gold > 0:
                if self.player.gold > self.stats.gold_max:
                    self.stats.gold_max = self.player.gold
                if self.player.gold < self.stats.gold_min:
                    self.stats.gold_min = self.player.gold
                if self.target_gold > 0 and self.player.gold >= self.target_gold:
                    end_reason = 'Reached target gold.'
                    break
            if self.hooks.end:
                end_reason = self.hooks.end_reason
                break

        # Update stats

        self.stats.gold_end = self.player.gold

        total = self.player.wins + self.player.losses + \
            self.player.ties + self.player.surrenders
        self.stats.total_hands = total
        self.stats.wins = self.player.wins
        self.stats.losses = self.player.losses
        self.stats.ties = self.player.ties
        self.stats.surrenders = self.player.surrenders
        self.stats.nat_wins = self.player.nats
        self.stats.nat_losses = self.player.natlosses
        self.stats.win_streak = self.player.winning_streak_max
        self.stats.loss_streak = self.player.losing_streak_max
        self.stats.tie_streak = self.player.tie_streak_max
        self.stats.surrender_streak = self.player.surrender_streak_max

        return (end_reason, self.stats)
