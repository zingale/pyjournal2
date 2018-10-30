"""routines to managing the git interactions for the journal"""

import os
import re
import sys
import shutil

import entry_util
import shell_util

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
        except:
            sys.exit("ERROR: you need to specify an existing path in which to create the journal repo")

    # create the bare git repo
    git_master = "{}/journal-{}.git".format(master_path, nickname)
    try:
        os.mkdir(git_master)
    except:
        sys.exit("ERROR: unable to create a directory in {}".format(master_path))

    os.chdir(git_master)
    shell_util.run("git init --bare")

    # create the local working copy
    try:
        os.chdir(working_path)
    except:
        sys.exit("ERROR: unable to change to {}".format(working_path))

    shell_util.run("git clone " + git_master)

    # create the initial directory structure
    working_journal = "{}/journal-{}".format(working_path, nickname)

    try:
        source_dir = os.path.abspath(os.path.join(defs["module_dir"], "sphinx_base/source"))
        shutil.copytree(source_dir, os.path.join(working_journal, "source"))
        shutil.copy(os.path.join(defs["module_dir"], "sphinx_base/Makefile"),
                working_journal)
    except:
        sys.exit("ERROR: unable to create initial directory structure")

    # create the journal_info.py
    with open(os.path.join(working_journal, "journal_info.py"), "w") as f:
        f.write("username = \"{}\"\n".format(username))
    #except:
    #    sys.exit("ERROR unable to write in initial directory structure")

    # create the .pyjournal2rc file
    try:
        with open(defs["param_file"], "w") as f:
            f.write("[{}]\n".format("main"))
            f.write("master_repo = {}\n".format(git_master))
            f.write("working_path = {}\n".format(working_path))
            f.write("nickname = {}\n".format(nickname))
            f.write("username = {}\n".format(username))
    except:
        sys.exit("ERROR: unable to open {} for appending".format(defs["param_file"]))

    defs["master_repo"] = git_master
    defs["working_path"] = working_path
    defs["nickname"] = nickname
    defs["username"] = username

    # create an initial entry saying "journal created"
    images = []
    entry_util.entry("main", images, defs, string="journal created\n")

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
        sys.exit("ERROR: the remote-git-repo should be of the form: ssh://machine/dir/journal-nickname.git")

    # make sure that a journal with this nickname doesn't already exist
    if nickname in defs.keys():
        sys.exit("ERROR: nickname already exists")

    # git clone the bare repo at master_repo into the working path
    try:
        os.chdir(working_path)
    except:
        sys.exit("ERROR: unable to switch to directory {}".format(working_path))

    _, stderr, rc = shell_util.run("git clone " + master_repo)
    if rc != 0:
        print(stderr)
        sys.exit("ERROR: something went wrong with the git clone")

    # create (or add to) the .pyjournalrc file
    try:
        f = open(defs["param_file"], "a+")
    except:
        sys.exit("ERROR: unable to open {} for appending".format(defs["param_file"]))

    f.write("[{}]\n".format(nickname))
    f.write("master_repo = {}\n".format(master_repo))
    f.write("working_path = {}\n".format(working_path))
    f.write("\n")
    f.close()



#=============================================================================
# general routines
#=============================================================================

def pull(defs, nickname=None):
    """pull the journal from the origin"""

    # switch to the working directory and pull from the master
    if nickname is not None:
        wd = "{}/journal-{}".format(defs[nickname]["working_path"], nickname)
    else:
        wd = "{}/todo_list".format(defs["working_path"])

    try:
        os.chdir(wd)
    except:
        sys.exit("ERROR: unable to switch to working directory: {}".format(wd))

    stdout, stderr, rc = shell_util.run("git pull")
    if rc != 0:
        print(stdout, stderr)
        sys.exit("ERROR: something went wrong with the git pull")

    print(stdout)


def push(defs, nickname=None):
    """push the journal to the origin"""

    # switch to the working directory and push to the master
    if nickname is not None:
        wd = "{}/journal-{}".format(defs[nickname]["working_path"], nickname)
    else:
        wd = "{}/todo_list".format(defs["working_path"])

    try:
        os.chdir(wd)
    except:
        sys.exit("ERROR: unable to switch to working directory: {}".format(wd))

    _, stderr, rc = shell_util.run("git push")
    if rc != 0:
        print(stderr)
        sys.exit("ERROR: something went wrong with the git push")

    print(stderr)
