"""This module controls writing an entry in the journal"""

import datetime
import os
import shutil
import sys

import pyjournal2.shell_util as shell_util

FIGURE_STR = r"""
.. _@figlabel@:
.. figure:: @figname@
   :scale: 80%
   :align: center

   The caption goes here

.. reference this as :numref:`@figlabel@`
"""

SYMBOLS = r"""
.. special characters: αβγδεζηθικλμνξοπρστυφχψω ΓΔΘΛΞΠΣΦΨΩ — ←→ ✓
.. you can add an entry to the index via '.. index:: key'"""

WARNING = '\033[93m'
SUCCESS = '\033[92m'
FAIL = '\033[91m'
BOLD = '\033[1m'
ENDC = '\033[0m'

def warning(ostr):
    """
    Output a string to the terminal colored orange to indicate a
    warning
    """
    print(WARNING + ostr + ENDC)


def success(ostr):
    """
    Output a string to the terminal colored green to indicate
    success
    """
    print(SUCCESS + ostr + ENDC)


#=============================================================================
# journal-specific routines
#=============================================================================

def get_dir_string():
    """get the new entry string in the form YYYY-MM-DD"""
    now = datetime.date.today()
    return str(now)

def get_unique_string():
    """get a full date time string"""
    now = datetime.datetime.now()
    return str(now.replace(microsecond=0)).replace(" ", "_").replace(":", ".")

def entry(topic, images, link_files, defs, string=None, use_date=None):
    """create an entry"""

    try:
        editor = os.environ["EDITOR"]
    except:
        editor = "emacs"


    if topic == "todo":
        odir = "{}/journal-{}/source/todo/".format(defs["working_path"],
                                                   defs["nickname"])
        ofile = "todo.rst"

    else:
        # determine the filename
        if use_date is not None:
            entry_dir = use_date
        else:
            entry_dir = get_dir_string()
        ofile = entry_dir + ".rst"

        # determine the directory we place it in -- this is the form yyyy-mm-dd/
        odir = "{}/journal-{}/source/{}/{}/".format(defs["working_path"],
                                                    defs["nickname"],
                                                    topic,
                                                    entry_dir)

    if not os.path.isdir(odir):
        try:
            os.mkdir(odir)
        except:
            sys.exit("ERROR: unable to make directory {}".format(odir))


    entry_file = os.path.join(odir, ofile)
    if not os.path.isfile(entry_file):
        if ofile == "todo.rst":
            header = len("todo")*"*" + "\n" + "todo\n" + len("todo")*"*" + "\n"
        else:
            header = ".. _{}_{}:\n\n".format(topic, entry_dir)
            header += len(entry_dir)*"*" + "\n" + "{}\n".format(entry_dir) + len(entry_dir)*"*" + "\n"
        header += SYMBOLS + "\n\n"
    else:
        header = ""

    # open (and create if necessary) the entry file.
    # If we passed in a string, then write it too.
    try:
        f = open(entry_file, "a+")
    except:
        sys.exit("ERROR: unable to open {}".format(os.path.join(odir, ofile)))

    f.write(header)
    if string is not None:
        f.write(string)

    # if there are images, then copy them over and add the figure
    # headings to the entry
    unique_id = get_unique_string()

    files_copied = []
    for im in images + link_files:

        if im is None:
            continue

        # does an file by that name already live in the dest
        # directory?
        src = im
        dest = odir

        im_copy = os.path.basename(im)
        if os.path.isfile("{}/{}".format(dest, im_copy)):
            im_copy = "{}_{}".format(unique_id.replace(".", "_"), im_copy)

        dest = os.path.join(dest, im_copy)

        # copy it
        if im != "":
            try:
                shutil.copy(src, dest)
            except:
                sys.exit("ERROR: unable to copy image {} to {}".format(src, dest))

            files_copied.append(im_copy)

            if im in images:
                # create a unique label for latex referencing
                idx = im_copy.lower().rfind(".jpg")
                idx = max(idx, im_copy.lower().rfind(".png"))
                idx = max(idx, im_copy.lower().rfind(".gif"))
                idx = max(idx, im_copy.lower().rfind(".pdf"))

                if idx >= 0:
                    im0 = "{}:{}".format(unique_id, im_copy[:idx])
                else:
                    sys.exit("unsupported image type -- try creating a link instead")

                # add the figure text
                for l in FIGURE_STR.split("\n"):
                    f.write("{}\n".format(
                        l.replace("@figname@", im_copy).replace("@figlabel@", im0).rstrip()))

            else:
                # add the download directive
                f.write(":download:`{} <{}>`\n\n".format(im_copy, im_copy))

    f.close()

    # launch the editor specified in the EDITOR environment variable
    if string is None:
        if editor == "emacs":
            prog = "emacs -nw {}/{}".format(odir, ofile)
        else:
            prog = "{} {}/{}".format(editor, odir, ofile)

        stdout, stderr, rc = shell_util.run(prog)

    # commit the entry to the working git repo
    os.chdir(odir)

    stdout, stderr, rc = shell_util.run("git add " + ofile)
    stdout, stderr, rc = shell_util.run("git commit -m 'new entry' " + ofile)

    # commit any images too
    for im in files_copied:
        stdout, stderr, rc = shell_util.run("git add " + im)
        stdout, stderr, rc = shell_util.run("git commit -m 'new image' " + im)
