import getopt
import sys
import time
import statistics
from simulator import simulator, strategy, betting, stats


BETTING_SYSTEMS = {
    "none": betting.NoBetting,
    "martingale": betting.Martingale,
    "flowplay": betting.FlowPlayBetting,
    "simple": betting.SimpleBetting
}


HELP_GENERAL = [
    (['-h', '--help'], ['print this help']),
    (['-v', '--verbose'], ['print a LOT of extra info']),
]


HELP_SIMULATOR = [
    (['-s', '--strat=FILE'], ['playing strategy file to use (default "strats/strat.txt")']),
    (['-i', '--iterations=ITS'],
     ['how many times to run the simulation until', 'an end condition is reached (default 1)']),
    (['-g', '--gold=GOLD'], ['total gold to start with, or 0 to disable gold',
                             'completely (default 0)']),
]


HELP_BETTING = [
    (['-b', '--bet-system=SYSTEM'], ['betting system to use (default "none")']),
    (['-o', '--bet-options=OPTS'],
     ['comma-separated key=value list of options', 'to pass to the betting system']),
    (['    --list-bet-systems'], ['list available betting systems']),
]


HELP_CONDITIONS = [
    (['-r', '--rounds=ROUNDS'], ['maximum number of rounds to run']),
    (['-t', '--target=GOLD'], ['target gold amount to reach']),
]


def print_help_thing(thing):
    """
    Prints a list of command line options with a description.

    :param thing: list of tuples containing a list of options and a list of description lines
    """
    for (cmds, desc) in thing:
        print("  {:<24}{}".format(", ".join(cmds), desc.pop(0)))
        for line in desc:
            print("  {:<24}{}".format('', line))


def usage(file):
    """
    Prints command help
    """
    print("Usage: {0} [OPTION...]".format(file))

    print("\nGeneral:")
    print_help_thing(HELP_GENERAL)
    print("\nSimulator:")
    print_help_thing(HELP_SIMULATOR)
    print("\nBetting:")
    print_help_thing(HELP_BETTING)
    print("\nEnd conditions:")
    print_help_thing(HELP_CONDITIONS)

    print("\n\nBetting systems:")
    print("  {}".format(", ".join(sorted(BETTING_SYSTEMS.keys()))))


def main():
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hvs:i:g:b:o:r:t:", [
            "help", "verbose", "strat=", "iterations=", "gold=", "bet-system=", "bet-options=", "list-bet-systems", "rounds=", "target="])
    except getopt.GetoptError as err:
        print(err)
        usage(sys.argv[0])
        sys.exit(2)

    verbose = False

    def verbose_print(*args):
        if verbose:
            print(*args)

    # Default options
    iterations = 1
    starting_gold = 0
    strat_file = "strats/strat.txt"

    bet_system_name = "none"
    bet_options = ""

    # End conditions, at least one should be enabled
    target_gold = 0
    rounds = 0

    for o, a in opts:
        if o == '-v':
            verbose = True
        elif o in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit()
        elif o in ('-s', '--strat'):
            strat_file = a
        elif o in ('-b', '--bet-system'):
            bet_system_name = a
        elif o in ('-o', '--bet-options'):
            bet_options = a
        elif o == '--list-bet-systems':
            print("Available betting systems:", ", ".join(
                sorted(BETTING_SYSTEMS.keys())))
            sys.exit()
        elif o in ('-i', '--iterations'):
            iterations = int(a)
        elif o in ('-r', '--rounds'):
            rounds = int(a)
        elif o in ('-g', '--gold'):
            starting_gold = int(a)
        elif o in ('-t', '--target'):
            target_gold = int(a)
        else:
            assert False, "unhandled option"

    strat = strategy.BlackjackStrategy.from_file(strat_file, out=verbose_print)

    if bet_system_name not in BETTING_SYSTEMS:
        print("Invalid betting system '{}'".format(bet_system_name))
        print("Available systems:", ", ".join(sorted(BETTING_SYSTEMS.keys())))
        sys.exit(1)

    bet_system = BETTING_SYSTEMS[bet_system_name].from_options(bet_options)

    if target_gold == 0 and rounds == 0:
        print("At least one end condition (--target or --rounds) needs to be enabled.")
        sys.exit(1)

    print("Casino Simulator 9000!")
    print("Using strat file:", strat_file)
    print("Using betting system:", bet_system_name)
    print("  with options:", bet_options)

    if starting_gold > 0:
        print()
        print("{:.<16}{:.>20,}".format("Starting gold", starting_gold))

    if target_gold > 0:
        print("{:.<16}{:.>20,}".format("Gold target", target_gold))

    print("{:.<16}{:.>20,}".format("Max rounds", rounds))

    print()
    print("Running {0} iterations of blackjack...".format(iterations))

    # Track stats over all iterations my merging each iteration's
    # own stats instance with this one
    total_stats = stats.BlackjackStats()
    total_stats.gold_start = starting_gold
    total_stats.gold_target = target_gold
    total_stats.gold_min = starting_gold

    bj = simulator.BlackjackSimulator(strat, bet_system, out=verbose_print)
    bj.set_starting_gold(starting_gold)
    bj.set_target_gold(target_gold)

    start = time.perf_counter()
    # Track the count of each iteration end reason, plus couple other per-reason
    # stats for displaying at the end
    reasons = {}
    for _ in range(0, iterations):
        bj.reset()

        (reason, st) = bj.run(rounds)
        # Merge stats with total
        total_stats.add(st)
        if reason not in reasons:
            reasons[reason] = {"count": 0, "gold_end": [], "hands": []}
        reasons[reason]["count"] += 1
        reasons[reason]["gold_end"].append(st.gold_end)
        reasons[reason]["hands"].append(st.total_hands)
    end = time.perf_counter()

    print("Completed in {:.2f}s".format(end - start))
    print()

    # Display end reasons and stats
    print("Results:")
    for rs in sorted(reasons.keys()):
        s = reasons[rs]
        print("  {:.<22}{:.>12,} ({:>6.2%})".format(
            rs, s["count"], s["count"]/iterations))
        # print(s["gold_end"])
        print("    {:.<16}{:.>16,.2f}".format(
            "Avg. end gold", statistics.mean(s["gold_end"])))
        print("    {:.<16}{:.>16,.2f}".format(
            "Avg. hands dealt", statistics.mean(s["hands"])))
    print("\nStats:")
    total_stats.print()


if __name__ == "__main__":
    main()
