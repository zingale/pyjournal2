#!/usr/bin/env python3

"""
a simple commandline-driven scientific journal in LaTeX managed by git
"""

import pyjournal2.main_util as main_util

if __name__ == "__main__":
    tdefs = main_util.read_config()
    targs = main_util.get_args(tdefs)
    main_util.main(targs, tdefs)

