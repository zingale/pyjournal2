# pyjournal2

pyjournal2 is a commandline script written in python to create and
manage a Sphinx ReST-based scientific journal.  The journal is
distributed (via `git`) so that we can access it from any machine we
work on.  It is commandline driven to make the barrier-to-entry for
creating a short entry minimal.  Entries are grouped into topics and
shown in date-order.

The basic idea is that you have one research journal with a number of
topics to organize ideas.  Each topic appears as a chapter in the
Sphinx web navigation bar, allowing you to easily switch between them.
Within a topic, entries are ordered chronologically, with one `.rst`
file per day.  Images and links to files can easily be added (and the
files are copied to the git repo so they are permanently part of the
journal).

Note: pyjournal2 requires python 3

* Installing:

  ```
  python3 setup.py install --user
  ```

  (omit the `--user` for a systemwide installation).  This will put the
  `pyjournal.py` executable script in you system's path.

  You should set your `EDITOR` environment variable.  This has been tested
  with emacs and vi.  For emacs, should should launch it in a terminal, e.g.,
  by setting

  ```
  export EDITOR="emacs -nw"
  ```

* Command help:

  pyjournal2 uses a number of subcommands to create, edit, and build a
  journal.  Doing:
  ```
  pyjournal.py --help
  ```
  will list all the commands.  Additional help for each of the commands
  can be found by doing
  ```
  pyjournal.py command --help
  ```
  for the command `command`.

* Starting:

  - `pyjournal.py init nickname username master-path [working-path]`

    this initializes a bare git repo that will hold the journal data,
    creates the initial directory structure to hold the journal
    entries, and copies in the Sphinx source hierarchy to get things
    started. It will also create a `.pyjournal2rc` file
    with an entry for this journal name (nickname).

    `master-path/` should be an existing directory.  The journal
	master repo will be created as a subdirectory under `master-path/`
	as a bare git repo.  The working clone that we interact with is
	placed there too, unless we specify the optional `working-path`
	argument.

    `usename` and journal `nickname` are needed only for the styling
    of the Sphinx output.

    The `git` operations that take place under the hood are:

      - Creating a bare repo for others to clone to/from:

        ```
        mkdir path/nickname.git
        cd path/nickname.git
        git init --bare
        ```

      - Creating the working directory that we will interact with:

        ```
        cd working-path/
        git clone path/nicknmae
        ```


  - `pyjournal.py connect remote-machine:/git-path/journal-nickname.git working-path`

    If you already established a journal on another machine (using the
    `init` action), then `connect` is used to create a clone of that
    journal on your local machine (if you are only working on a single
    machine, then you don't need to do this).

    Note that for the remote git repo is specified in the same way you
    would specify a remote git repo for `git clone`.  This points to
    the remote bare repo.

    Only a working repo is stored locally (created though a `git clone`).


* Day-to-day use:

  - `pyjournal.py entry [--link link-files] [topic] [images [images ...]]`

    adds an entry to the journal under the topic `topic`.  If `topic`
    is not included, then the entry is put in the default `main` topic.
    Any number of image files can be appended to the `entry` line---these
    will be copied into the journal and a Sphinx figure directive will
    be setup for you when the entry pops up in your editor.

    There is a single entry per day for each topic, so running `entry`
    again will allow you to continue editing the same entry.

    Some shortcuts exist for entries:

      * if you just want to do an entry to the main topic with no
        images, you can simply type `pyjournal.py` without any
        arguments.

      * if you want to create an entry in an existing topic, you can
        just do `pyjournal.py topic`, omitting the word `entry`.

    To create a new topic, simply do:

    ```pyjournal entry new-topic-name```

    you will then be prompted if you really want to create the new topic,
    and if you answer yes, the editor will pop up with a blank entry
    page in the new topic.

  - `pyjournal.py build`

    builds the journal Sphinx webpage

  - `pyjournal.py show`

    builds the journal webpage and opens it in a tab of your existing
    web browswer.

  - `pyjournal.py pull`

    gets any changes from the master version of the journal (remote
    git bare repository)

  - `pyjournal.py push`

    pushes any changes in the local journal to the remote (git bare
    repo) version

  - `pyjournal.py continue topic-name`

    continues editing the previous entry for a topic.  This is only
    needed if you want to continue an entry from the previous day.
    Otherwise, `pyjournal.py topic-name` will always continue the
    current day's entry.

