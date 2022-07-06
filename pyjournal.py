#!/usr/bin/env python3

"""
a simple commandline-driven scientific journal in LaTeX managed by git
"""

from pyjournal2 import main_util

if __name__ == "__main__":
    tdefs = main_util.read_config()
    targs = main_util.get_args(tdefs)
    main_util.main(targs, tdefs)
