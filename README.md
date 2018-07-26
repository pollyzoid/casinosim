# CasinoSim

## Usage

```text
Usage: casinosim.py [OPTION...]

General:
  -h, --help              print this help
  -v, --verbose           print a LOT of extra info
  -f, --out-file          output the results to a file

Simulator:
  -s, --strat=FILE        playing strategy file to use (default "strats/strat.txt")
  -i, --iterations=ITS    how many times to run the simulation until
                          an end condition is reached (default 1)
  -g, --gold=GOLD         total gold to start with, or 0 to disable gold
                          completely (default 0)
      --threads           how many processes to run the simulation on (default 0 = auto)
      --anti-fallacy      enable anti-fallacy strat (after a loss, bet 0 until a win, repeat)

Betting:
  -b, --bet-system=SYSTEM betting system to use (default "none")
  -o, --bet-options=OPTS  comma-separated key=value list of options
                          to pass to the betting system
  -p, --positive-prog     use positive progression instead of negative
      --list-bet-systems  list available betting systems

End conditions:
  -r, --rounds=ROUNDS     maximum number of rounds to run
  -t, --target=GOLD       target gold amount to reach


Betting systems:
  fibonacci, fp, idkmartingale, labouchere, martingale, none, simple
```

## Examples

### Simple betting (bet same amount every round)

```shell
python casinosim.py --iterations=100 --gold=10000 --target=12000 --bet-system=simple --bet-options=bet=500
```

### Normal martingale betting

```shell
python casinosim.py --iterations=100 --rounds=100 --gold=10000 --target=12000 --bet-system=martingale --bet-options=starting-bet=100
```

### Fibonacci betting

```shell
python casinosim.py --iterations=100 --gold=10000 --target=12000 --bet-system=fibonacci --bet-options=starting-bet=100
```

### Reversed fibonacci betting

```shell
python casinosim.py --iterations=100 --positive-prog --gold=15000 --target=16000 --bet-system=fibonacci --bet-options=starting-bet=100
```

### FPBetting, output written into sim.log

```shell
python casinosim.py --out-file=sim.log --iterations=100 --gold=100000 --target=120000 --bet-system=fp --bet-options=stacks=3,levels=5,stack-multi=2.223,bet-multi=2.223
```

### Two-way martingale

```shell
python casinosim.py --iterations=1000 --gold=12000 --target=14000 --bet-system=idkmartingale --bet-options=starting-bet=100
```

### Labouchere

```shell
python casinosim.py --iterations=2000 --gold=240000 --target=280000 --bet-system=labouchere --bet-options=starting-bet=1000,seq=1-2-3-5-8-3-2
```