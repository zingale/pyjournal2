"""routines to managing the git interactions for the journal"""

import os
import re
import sys
import shutil

from pyjournal2 import entry_util
from pyjournal2 import shell_util

#=============================================================================
# journal-specific routines
#=============================================================================


def init(nickname, username, master_path, working_path, defs):
    """initialize the journal by setting up the git repo and copying the
    basic sphinx directory tree"""

    # make sure we have absolute paths
    working_path = os.path.abspath(working_path)

    # we are create the directory beneath master_path/, so make sure that
    # exists
    master_path = os.path.abspath(master_path)

    if not os.path.isdir(master_path):
        try:
            os.mkdir(master_path)
        except (FileExistsError, FileNotFoundError):
            sys.exit("ERROR: you need to specify an existing path in which to create the journal repo")

    # create the bare git repo
    git_master = f"{master_path}/journal-{nickname}.git"
    try:
        os.mkdir(git_master)
    except (FileExistsError, FileNotFoundError):
        sys.exit(f"ERROR: unable to create a directory in {master_path}")

    os.chdir(git_master)
    shell_util.run("git init --bare")

    # create the local working copy
    try:
        os.chdir(working_path)
    except OSError:
        sys.exit(f"ERROR: unable to change to {working_path}")

    shell_util.run("git clone " + git_master)

    # create the initial directory structure
    working_journal = f"{working_path}/journal-{nickname}"

    try:
        source_dir = os.path.abspath(os.path.join(defs["module_dir"], "sphinx_base/source"))
        shutil.copytree(source_dir, os.path.join(working_journal, "source"))
        shutil.copy(os.path.join(defs["module_dir"], "sphinx_base/Makefile"),
                working_journal)
    except OSError:
        sys.exit("ERROR: unable to create initial directory structure")

    # create the .pyjournal2rc file
    try:
        with open(defs["param_file"], "w") as f:
            f.write("[main]\n")
            f.write(f"master_repo = {git_master}\n")
            f.write(f"working_path = {working_path}\n")
            f.write(f"nickname = {nickname}\n")
            f.write(f"username = {username}\n")
    except OSError:
        sys.exit(f"ERROR: unable to open {defs['param_file']} for appending")

    defs["master_repo"] = git_master
    defs["working_path"] = working_path
    defs["nickname"] = nickname
    defs["username"] = username

    # create an initial entry saying "journal created"
    images = []
    link_file = []
    entry_util.entry("main", images, link_file, defs, string="journal created\n")

    # do a git add / push
    os.chdir(working_journal)

    shell_util.run("git add .")
    shell_util.run("git commit -m 'initial journal.tex file' .")
    shell_util.run("git push origin master")


def connect(master_repo, working_path, defs):
    """connect to an existing journal on git on another machine"""

    # get the nickname from the master repo name
    re_name = r"journal-(.*).git"
    a = re.search(re_name, master_repo)

    if a is not None:
        nickname = a.group(1)
    else:
        sys.exit("ERROR: the remote-git-repo should be of the form: machine:/dir/journal-nickname.git")

    # make sure that a journal does not already exist
    if os.path.isfile(defs["param_file"]):
        sys.exit("ERROR: a journal already exists")

    # git clone the bare repo at master_repo into the working path
    try:
        os.chdir(working_path)
    except OSError:
        sys.exit(f"ERROR: unable to switch to directory {working_path}")

    _, stderr, rc = shell_util.run("git clone " + master_repo)
    if rc != 0:
        print(stderr)
        sys.exit("ERROR: something went wrong with the git clone")

    # create (or add to) the .pyjournal2rc file
    try:
        with open(defs["param_file"], "w") as f:
            f.write("[main]\n")
            f.write(f"master_repo = {master_repo}\n")
            f.write(f"working_path = {working_path}\n")
            f.write(f"nickname = {nickname}\n")
    except OSError:
        sys.exit(f"ERROR: unable to open {defs['param_file']} for appending")


#=============================================================================
# general routines
#=============================================================================


def pull(defs, nickname=None):
    """pull the journal from the origin"""

    wd = f"{defs['working_path']}/journal-{defs['nickname']}"

    try:
        os.chdir(wd)
    except OSError:
        sys.exit(f"ERROR: unable to switch to working directory: {wd}")

    stdout, stderr, rc = shell_util.run("git pull")
    if rc != 0:
        print(stdout, stderr)
        sys.exit("ERROR: something went wrong with the git pull")

    print(stdout)


def push(defs, nickname=None):
    """push the journal to the origin"""

    # switch to the working directory and push to the master
    wd = f"{defs['working_path']}/journal-{defs['nickname']}"

    try:
        os.chdir(wd)
    except OSError:
        sys.exit(f"ERROR: unable to switch to working directory: {wd}")

    _, stderr, rc = shell_util.run("git push")
    if rc != 0:
        print(stderr)
        sys.exit("ERROR: something went wrong with the git push")

    print(stderr)
