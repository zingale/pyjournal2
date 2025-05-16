"""routines for interacting with the command shell"""

import shlex
import subprocess


def run(string):
    """run a command and capture the output and return code"""

    stdout = None
    stderr = None
    rc = None

    # shlex.split will preserve inner quotes
    prog = shlex.split(string)
    if prog[0] == "vi":
        # vi hangs when piping stdout/stderr
        p0 = subprocess.Popen(prog)
        stdout0, stderr0 = p0.communicate()
        rc = p0.returncode

    else:
        p0 = subprocess.Popen(prog, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        stdout0, stderr0 = p0.communicate()
        rc = p0.returncode
        stdout = stdout0.decode('utf-8')
        stderr = stderr0.decode('utf-8')

    return stdout, stderr, rc
