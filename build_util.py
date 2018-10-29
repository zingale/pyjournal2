import calendar
import os
import sys
import webbrowser

import shell_util

def build(defs, show=0):

    source_dir = "{}/journal-{}/source/".format(defs["working_path"], defs["nickname"])

    topics = []

    # get the list of directories in source/ -- these are the topics
    for d in os.listdir(source_dir):
        if os.path.isdir(os.path.join(source_dir, d)) and not d.startswith("_"):
            topics.append(d)

    print("topics: ", topics)

    # for each topic, we want to create a "topic.rst" that then has
    # things subdivided by year-month, and that a
    # "topic-year-month.rst" that includes the individual entries
    for topic in topics:
        tdir = os.path.join(source_dir, topic)
        os.chdir(tdir)

        # look over the directories here, they will be in the form YYYY-MM-DD
        years = []
        entries = []
        for d in os.listdir(tdir):
            if os.path.isdir(os.path.join(tdir, d)):
                y, _, _ = d.split("-")
                if y not in years:
                    years.append(y)
                entries.append(d)

        years.sort()
        entries.sort()
        print(entries)

        # we need to create ReST files of the form YYYY.rst.  These
        # will each then contain the links to the entries for that
        # year
        for y in years:
            y_entries = [q for q in entries if q.startswith(y)]

            with open("{}.rst".format(y), "w") as yf:
                yf.write("****\n")
                yf.write("{}\n".format(y))
                yf.write("****\n\n")

                yf.write(".. toctree::\n")
                yf.write("   :maxdepth: 2\n")
                yf.write("   :caption: Contents:\n\n")

                for entry in y_entries:
                    yf.write("   {}/{}.rst\n".format(entry, entry))

        # now write the topic.rst
        with open("{}.rst".format(topic), "w") as tf:
            tf.write(len(topic)*"*" + "\n")
            tf.write("{}\n".format(topic))
            tf.write(len(topic)*"*" + "\n")

            tf.write(".. toctree::\n")
            tf.write("   :maxdepth: 2\n")
            tf.write("   :caption: Contents:\n\n")

            for y in years:
                tf.write("   {}.rst\n".format(y))


    # now write the index.rst
    os.chdir(source_dir)
    with open("index.rst", "w") as mf:
        mf.write("Research Journal\n")
        mf.write("================\n\n")
        mf.write(".. toctree::\n")
        mf.write("   :maxdepth: 2\n")
        mf.write("   :caption: Contents:\n\n")

        for topic in topics:
            mf.write("   {}/{}\n".format(topic, topic))

        mf.write("\n")
        mf.write("Indices and tables\n")
        mf.write("==================\n\n")
        mf.write("* :ref:`genindex`\n")
        mf.write("* :ref:`modindex`\n")
        mf.write("* :ref:`search`\n")


    # now do the building
    build_dir = "{}/journal-{}/".format(defs["working_path"], defs["nickname"])
    os.chdir(build_dir)

    stdout, stderr, rc = shell_util.run("make html")

    if rc != 0:
        print("build may have been unsuccessful")

    index = os.path.join(build_dir, "build/html/index.html")

    # use webbrowser module
    if show == 1:
        webbrowser.open_new_tab(index)
