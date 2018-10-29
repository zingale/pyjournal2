import calendar
import os
import sys

import shell_util

def build(nickname, defs, show=0):

    entry_dir = "{}/journal-{}/entries/".format(defs[nickname]["working_path"], nickname)

    entries = []
    years = []

    # get the list of directories in entries/
    for d in os.listdir(entry_dir):
        if os.path.isdir(entry_dir + d):
            entries.append(d)

            y, m, d = d.split("-")
            if not y in years:
                years.append(y)


    os.chdir(entry_dir)

    years.sort()
    entries.sort()

    # years are chapters
    try: f = open("chapters.tex", "w")
    except:
        sys.exit("ERROR: unable to create chapters.tex")


    for y in years:
        f.write("\\chapter{{{}}}\n".format(y))
        f.write("\\input{{entries/{}.tex}}\n\n".format(y))


    f.close()


    # within each year, months are sections
    for y in years:

        try: f = open("{}.tex".format(y), "w")
        except:
            sys.exit("ERROR: unable to create chapters.tex")

        current_month = None
        current_day = None

        for e in entries:
            ytmp, m, d = e.split("-")
            if not ytmp == y:
                continue

            if not m == current_month:
                f.write("\\section{{{}}}\n".format(calendar.month_name[int(m)]))
                current_month = m

            tex = []
            for t in os.listdir(e):
                if t.endswith(".tex"):
                    tex.append(t)

            tex.sort()
            for t in tex:
                if not d == current_day:
                    f.write("\\subsection{{{} {}}}\n".format(calendar.month_name[int(m)], d))
                    current_day = d

                f.write("\\HRule\\\\ \n")
                idx = t.rfind(".tex")
                tout = t[:idx].replace("_", " ")
                f.write("{{\\bfseries {{\sffamily {} }} }}\\\\[0.5em] \n".format(tout))
                f.write("\\input{{entries/{}/{}}}\n\n".format(e, t))
                f.write("\\vskip 2em\n")

            f.write("\n")

        f.close()

    # now do the latexing to get the PDF
    build_dir = "{}/journal-{}/".format(defs["working_path"], defs["nickname"])
    os.chdir(build_dir)

    stdout, stderr, rc = shell_util.run("make html")

    if rc != 0:
        print("build may have been unsuccessful")

    index = os.path.join(build_dir, "build/html/index.html")

    # use webbrowser module
    if show == 1:
        webbrowser.open_new_tab(index)
