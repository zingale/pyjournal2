from __future__ import print_function

import datetime
import hashlib
import os
import shutil
import sys

import shell_util

figure_str = r"""
\begin{figure}[h]
\centering
\includegraphics[width=0.5\linewidth]{@figname@}
\caption{\label{fig:@figlabel@} caption goes here}
\end{figure}

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

def get_entry_string():
    now = datetime.datetime.now()
    return str(now.replace(microsecond=0)).replace(" ", "_").replace(":", ".")


def get_dir_string():
    now = datetime.date.today()
    return str(now)


def entry(nickname, images, defs, string=None):

    try: editor = os.environ["EDITOR"]
    except:
        editor = "emacs"

    # determine the filename
    entry_id = get_entry_string()
    entry_dir = get_dir_string()
    ofile = entry_id + ".tex"

    # determine the directory we place it in -- this is the form yyyy-mm-dd/
    odir = "{}/journal-{}/entries/{}/".format(defs[nickname]["working_path"],
                                              nickname,
                                              entry_dir)

    if not os.path.isdir(odir):
        try: os.mkdir(odir)
        except:
            sys.exit("ERROR: unable to make directory {}".format(odir))


    # create the entry file.  If we passed in a string, then write it
    # too.
    try: f = open(odir + ofile, "w")
    except:
        sys.exit("ERROR: unable to open {}".format(odir + ofile))

    if string is not None:
        f.write(string)
    else:
        f.write("% journal: {}\n".format(nickname))


    # if there are images, then copy them over and add the figure
    # headings to the entry
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
        idx = im.lower().rfind(".jpg")
        idx = max(idx, im.lower().rfind(".png"))
        idx = max(idx, im.lower().rfind(".pdf"))

        if idx >= 0:
            im0 = "{}:{}".format(entry_id, im[:idx])

        fname = "entries/{}/{}".format(entry_dir, im_copy)
        # add the figure text
        for l in figure_str.split("\n"):
            f.write("{}\n".format(
                l.replace("@figname@", fname).replace("@figlabel@", im0).rstrip()))

    # add the entry id as a LaTeX comment
    f.write("\n\n% entry: {}".format(entry_id))

    f.close()

    # get the hash for the file
    hash_orig = hashlib.md5(open(odir + ofile, 'r').read().encode('utf-8')).hexdigest()


    # launch the editor specified in the EDITOR environment variable
    if string == None:
        if editor == "emacs":
            prog = "emacs -nw {}/{}".format(odir, ofile)
        else:
            prog = "{} {}/{}".format(editor, odir, ofile)

        stdout, stderr, rc = shell_util.run(prog)


    # did the user actually make edits?
    hash_new = hashlib.md5(open(odir + ofile, 'r').read().encode('utf-8')).hexdigest()

    if string == None and len(images) == 0 and (hash_new == hash_orig):
        # user didn't do anything interesting
        answer = input("no input made -- add this to the journal? (y/N) ")
        if answer.lower() != "y":
            try: os.remove(odir + ofile)
            except:
                sys.exit("ERROR: unable to remove file -- entry aborted")

            sys.exit("entry aborted")


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

