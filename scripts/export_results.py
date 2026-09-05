import sys

from autonomy_evals.cli import main

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "export-results"] + ([]) + sys.argv[1:]
    main()
