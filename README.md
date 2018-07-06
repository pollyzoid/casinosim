# CasinoSim

## Usage

```text
Usage: casinosim.py [OPTION...]

General:
  -h, --help              print this help
  -v, --verbose           print a LOT of extra info

Simulator:
  -s, --strat=FILE        playing strategy file to use (default "strats/strat.txt")
  -i, --iterations=ITS    how many times to run the simulation until
                          an end condition is reached (default 1)
  -g, --gold=GOLD         total gold to start with, or 0 to disable gold
                          completely (default 0)

Betting:
  -b, --bet-system=SYSTEM betting system to use (default "none")
  -o, --bet-options=OPTS  comma-separated key=value list of options
                          to pass to the betting system
      --list-bet-systems  list available betting systems

End conditions:
  -r, --rounds=ROUNDS     maximum number of rounds to run
  -t, --target=GOLD       target gold amount to reach


Betting systems:
  fp, martingale, none, simple
```

## Examples

```shell
python casinosim.py --iterations=100 --rounds=100 --gold=10000 --target=12000 --bet-system=martingale --bet-options=starting-bet=100
```

```shell
python casinosim.py --iterations=100 --rounds=100 --gold=100000 --target=120000 --bet-system=fp --bet-options=stacks=3,levels=5,stack-multi=2.223,bet-multi=2.223
```
