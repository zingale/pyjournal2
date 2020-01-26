"""This module controls building the journal from the entry sources"""

import os
import webbrowser

import pyjournal2.shell_util as shell_util

def get_source_dir(defs):
    """return the directory where we put the sources"""
    return "{}/journal-{}/source/".format(defs["working_path"], defs["nickname"])

def get_topics(defs):
    """return a list of the currently known topics"""

    source_dir = get_source_dir(defs)

    topics = []
    other = []

    # get the list of directories in source/ -- these are the topics
    for d in os.listdir(source_dir):
        if os.path.isdir(os.path.join(source_dir, d)) and not d.startswith("_"):
            topics.append(d)

    # remove todo -- it will be treated specially
    if "todo" in topics:
        topics.remove("todo")
        other.append("todo")

    if "year_review" in topics:
        topics.remove("year_review")
        other.append("year_review")

    return topics, other

def get_topic_entries(topic, defs):

    cwd = os.getcwd()

    source_dir = get_source_dir(defs)
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

    os.chdir(cwd)

    return years, entries


def get_year_review_entries(defs):

    cwd = os.getcwd()

    source_dir = get_source_dir(defs)
    tdir = os.path.join(source_dir, "year_review")

    os.chdir(tdir)

    # look over the directories here, they will be in the form YYYY-MM-DD
    entries = []
    for f in os.listdir(tdir):
        if f.endswith(".rst") and f != "years.rst":
            entries.append(f)

    entries.sort()

    os.chdir(cwd)

    return entries


def create_topic(topic, defs):
    """create a new topic directory"""

    source_dir = get_source_dir(defs)
    try:
        os.mkdir(os.path.join(source_dir, topic))
    except:
        sys.error("unable to create a new topic")

def build(defs, show=0):
    """build the journal.  This entails writing the TOC files that link to
    the individual entries and then running the Sphinx make command

    """

    source_dir = get_source_dir(defs)

    topics, other = get_topics(defs)

    # for each topic, we want to create a "topic.rst" that then has
    # things subdivided by year-month, and that a
    # "topic-year-month.rst" that includes the individual entries
    for topic in topics:

        years, entries = get_topic_entries(topic, defs)
        tdir = os.path.join(source_dir, topic)
        os.chdir(tdir)

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

    # handle the year review now
    if "year_review" in other:
        tdir = os.path.join(source_dir, "year_review")
        os.chdir(tdir)
        entries = get_year_review_entries(defs)

        with open("years.rst", "w") as tf:
            topic = "year review"
            tf.write(len(topic)*"*" + "\n")
            tf.write("{}\n".format(topic))
            tf.write(len(topic)*"*" + "\n")

            tf.write(".. toctree::\n")
            tf.write("   :maxdepth: 2\n")
            tf.write("   :caption: Contents:\n\n")

            for e in entries:
                tf.write("   {}\n".format(e))


    # now write the index.rst
    os.chdir(source_dir)
    with open("index.rst", "w") as mf:
        mf.write("Research Journal\n")
        mf.write("================\n\n")
        mf.write(".. toctree::\n")
        mf.write("   :maxdepth: 1\n")
        mf.write("   :caption: Contents:\n\n")

        if "todo" in other:
            mf.write("   todo/todo.rst\n")

        if "year_review" in other:
            mf.write("   year_review/years.rst\n")

        for topic in sorted(topics):
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

    _, _, rc = shell_util.run("make clean")
    _, _, rc = shell_util.run("make html")

    if rc != 0:
        print("build may have been unsuccessful")

    index = os.path.join(build_dir, "build/html/index.html")

    # use webbrowser module
    if show == 1:
        webbrowser.open_new_tab(index)
