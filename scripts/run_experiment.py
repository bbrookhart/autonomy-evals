import sys

from autonomy_evals.cli import main

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "run"] + ([]) + sys.argv[1:]
    main()
