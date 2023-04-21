import sys
from pylint import lint

THRESHOLD = 8

if len(sys.argv) < 2:
    raise Exception("Module to evaluate needs to be the first argument")

run = lint.Run([sys.argv[1]], do_exit=False)
score = round(run.linter.stats.global_note, 2)

if score < THRESHOLD:
    print("Linter score is too low: ", score)
    sys.exit(1)
