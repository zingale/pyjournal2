#!/usr/bin/env python3

"""
a simple commandline-driven scientific journal in LaTeX managed by git
"""

from __future__ import print_function

import argparse
import configparser
import os
import sys

import build_util
import entry_util
import git_util

def get_args():
    """ parse the commandline arguments """

    # short circuit -- if there are no arguments, then we default to
    # entry, and we don't take any arguments, and we don't do an
    # argparse

    if len(sys.argv) == 1:  # the command name is first argument
        args = {"command": "entry",
                "images": [],
                "n": None}
    else:
        p = argparse.ArgumentParser()
        sp = p.add_subparsers(title="subcommands",
                              description="valid subcommands",
                              help="subcommands (use -h to see options for each)",
                              dest="command")

        # the init command
        init_ps = sp.add_parser("init", help="initialize a journal")
        init_ps.add_argument("nickname", help="name of the journal",
                             nargs=1, default=None, type=str)
        init_ps.add_argument("username", help="your name",
                             nargs=1, default=None, type=str)
        init_ps.add_argument("master-path",
                             help="path where we will store the master (bare) git repo",
                             nargs=1, default=None, type=str)
        init_ps.add_argument("working-path",
                             help="path where we will store the working directory (clone of bare repo)",
                             nargs="?", default=None, type=str)

        # the connect command
        connect_ps = sp.add_parser("connect",
                                   help="create a local working copy of a remote journal")
        connect_ps.add_argument("remote-git-repo",
                                help="the full path to the remote '.git' bare repo",
                                nargs=1, default=None, type=str)
        connect_ps.add_argument("working-path",
                                help="the (local) path where we will store the working directory",
                                nargs=1, default=None, type=str)

        # the entry command
        entry_ps = sp.add_parser("entry",
                                 help="add a new entry, with optional images")
        entry_ps.add_argument("topic", help="the name of the topic to add to",
                              nargs="*", default="main", type=str)
        entry_ps.add_argument("images", help="images to include as figures in the entry",
                              nargs="*", default=None, type=str)


        # the list command
        list_ps = sp.add_parser("list",
                                help="list the recent entry id's and .tex file path for the last entries")
        list_ps.add_argument("-N", help="number of entries to list",
                             type=int, default=10)

        # the build command
        build_ps = sp.add_parser("build",
                                 help="build a PDF of the journal")

        # the pull command
        pull_ps = sp.add_parser("pull",
                                help="pull from the remote journal" )

        # the push command
        push_ps = sp.add_parser("push",
                                help="push local changes to the remote journal")

        # the status command
        stat_ps = sp.add_parser("status",
                                help="list the current journal information")

        # the show command
        show_ps = sp.add_parser("show",
                                help="build the PDF and launch a PDF viewer")

        args = vars(p.parse_args())

    return args

def read_config():
    """ parse the .pyjournal2rc file -- store the results in a dictionary
        e.g., defs["working_path"] """
    defs = {}
    defs["param_file"] = os.path.expanduser("~") + "/.pyjournal2rc"
    defs["image_dir"] = os.getcwd()
    defs["module_dir"] = os.path.abspath(os.path.dirname(__file__))

    if os.path.isfile(defs["param_file"]):
        cp = configparser.ConfigParser()
        cp.optionxform = str
        cp.read(defs["param_file"])

        defs["working_path"] = cp.get("main", "working_path")
        defs["master_repo"] = cp.get("main", "master_repo")
        defs["nickname"] = cp.get("main", "nickname")
        defs["username"] = cp.get("main", "username")

    return defs

def main(args, defs):
    """ main interface """

    action = args["command"]

    if action == "init":
        nickname = args["nickname"][0]
        username = args["username"][0]
        master_path = args["master-path"][0]
        working_path = args["working-path"]
        if working_path == None:
            working_path = master_path

        master_path = os.path.normpath(os.path.expanduser(master_path))
        working_path = os.path.normpath(os.path.expanduser(working_path))

        git_util.init(nickname, username, master_path, working_path, defs)

    elif action == "connect":
        master_repo = args["remote-git-repo"][0]
        working_path = args["working-path"][0]
        working_path = os.path.normpath(os.path.expanduser(working_path))

        git_util.connect(master_repo, working_path, defs)

    elif action == "entry":
        images = args["images"]
        topic = args["topic"]
        entry_util.entry(topic, images, defs)

    elif action == "list":
        # options: number to list (optional)
        num = args["N"]
        entry_util.elist(num, defs)

    elif action == "build":
        build_util.build(defs)

    elif action == "show":
        build_util.build(defs, show=1)

    elif action == "pull":
        git_util.pull(defs)

    elif action == "push":
        git_util.push(defs)

    elif action == "status":

        print("pyjournal")
        print("  working directory: {}/journal-{}".format(defs["working_path"], nickname))
        print("  master git repo: {}".format(defs["master_repo"], nickname))
        print(" ")

    else:
        # we should never land here, because of the choices argument
        # to actions in the argparser
        sys.exit("invalid action")


if __name__ == "__main__":
    args = get_args()
    defs = read_config()
    main(args, defs)
