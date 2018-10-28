from __future__ import print_function

import datetime
import hashlib
import os
import shutil
import sys

import shell_util

figure_str = r"""
.. _@figlabel@:
.. figure:: @figname@
   :scale: 80%
   :align: center

   The caption goes here\centering

.. reference this as :numref:`@figlabel@`
"""

class _TermColors(object):
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
    print(_TermColors.WARNING + ostr + _TermColors.ENDC)


def success(ostr):
    """
    Output a string to the terminal colored green to indicate
    success
    """
    print(_TermColors.SUCCESS + ostr + _TermColors.ENDC)


#=============================================================================
# journal-specific routines
#=============================================================================

def get_dir_string():
    now = datetime.date.today()
    return str(now)

def get_entry_string():
    now = datetime.datetime.now()
    return str(now.replace(microsecond=0)).replace(" ", "_").replace(":", ".")

def entry(topic, images, defs, string=None):

    try: editor = os.environ["EDITOR"]
    except:
        editor = "emacs"

    # determine the filename
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


    # open (and create if necessary) the entry file.
    # If we passed in a string, then write it too.
    try:
        f = open(os.path.join(odir, ofile), "a+")
    except:
        sys.exit("ERROR: unable to open {}".format(os.path.join(odir, ofile)))

    if string is not None:
        f.write(string)

    # if there are images, then copy them over and add the figure
    # headings to the entry
    entry_id = get_entry_string()

    images_copied = []
    for im in images:

        # does an image by that name already live in the dest
        # directory?
        src = "{}/{}".format(defs["image_dir"], im)
        dest = odir

        if os.path.isfile("{}/{}".format(dest, im)):
            im_copy = "{}_{}".format(entry_id.replace(".", "_"), im)
        else:
            im_copy = im

        dest = "{}/{}".format(dest, im_copy)

        # copy it
        try: shutil.copy(src, dest)
        except:
            sys.exit("ERROR: unable to copy image {} to {}".format(src, dest))

        images_copied.append(im_copy)

        # create a unique label for latex referencing
        idx = im_copy.lower().rfind(".jpg")
        idx = max(idx, im_copy.lower().rfind(".png"))
        idx = max(idx, im_copy.lower().rfind(".pdf"))

        if idx >= 0:
            im0 = "{}:{}".format(entry_id, im[:idx])

        fname = "entries/{}/{}".format(entry_dir, im_copy)
        # add the figure text
        for l in figure_str.split("\n"):
            f.write("{}\n".format(
                l.replace("@figname@", fname).replace("@figlabel@", im0).rstrip()))

    f.close()

    # launch the editor specified in the EDITOR environment variable
    if string == None:
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
    for im in images_copied:
        stdout, stderr, rc = shell_util.run("git add " + im)
        stdout, stderr, rc = shell_util.run("git commit -m 'new image' " + im)


def elist(nickname, num, defs, print_out=True):

    entry_dir = "{}/journal-{}/entries/".format(defs[nickname]["working_path"], nickname)
    entries = {}
    for d in os.listdir(entry_dir):
        if os.path.isdir(entry_dir + d):

            edir = os.path.normpath("{}/{}".format(entry_dir, d))

            for t in os.listdir(edir):
                if t.endswith(".tex") and not "appendices" in edir:
                    entries[t] = "{}/{}".format(edir, t)

    e = list(entries.keys())
    e.sort(reverse=True)

    last_entries = []
    for n in range(min(num, len(e))):
        idx = e[n].rfind(".tex")
        entry_id = e[n][:idx]
        last_entries.append((entry_id, entries[e[n]]))

    if print_out:
        for e in last_entries:
            print("{} : {}".format(e[0], e[1]))
    else:
        return last_entries

