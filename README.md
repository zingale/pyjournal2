# pyjournal2

pyjournal2 is a commandline script written in python to create and
manage a Sphinx ReST-based scientific journal.  The journal is
distributed (via `git`) so that we can access it from any machine we
work on.  It is commandline driven to make the barrier-to-entry for
creating a short entry minimal.  Entries are groups into topics and
shown in date-order.

Note: pyjournal2 requires python 3

* Installing:

  Simply clone the git repo and put the directory in your path.
  Alternately, if you have a `~/bin/` directory, do:

  ```
  ln -s ~/{pyjournal-path}/pyjournal.py ~/bin/
  ```

  For the simplest (and laziest) access, create an alias `pj` for
  `pyjournal.py`


* Starting:

  - `pyjournal.py init nickname path/ [working-path]`

    this initializes a bare git repo that will hold the journal data,
    creates the initial directory structure to hold the journal
    entries, and copies in the master journal.tex file.  It will also
    add to (or create) a `.pyjournal2rc` file with an entry for this
    journal name (nickname).

    `path/` should be an existing directory.  The journal master repo
	will be created as a subdirectory under `path/` as a bare git
	repo.  The working clone that we interact with is placed there
	too, unless we specify the optional `working-path` argument.

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


  - `pyjournal.py connect ssh://remote-machine:/git-path/journal-nickname.git local-path`

    If you already established a journal on another machine (using the
    `init` action, then `connect` is used to create a clone of that
    journal on your local machine (if you are only working on a single
    machine, then you don't need to do this).

    Note that for the remote git repo is specified as the complete path
    (including the `ssh://` prefix) to the `.git` bare repo.  The nickname
    for the journal is taken from the repo name.

    Only a working repo is stored locally (created though a `git clone`).
    In this case, your `.pyjournalrc` will look like:

    ```
    [nickname]
    master_path = ssh://remote-machine:/git-path/git-repo.git
    working_path = local-path/
    ```


* Directory structure:

  ```
  journal-nickname/


   main/
      yyyy-mm-dd/
        yyy-mm-dd-hh-ss.rst
        ...
      yyyy-mm-dd/
	    ...

  ```


* Day-to-day use:

  - `pyjournal.py entry [-n nickname] [XXX [YYY ...]]`

    adds an entry to the journal (optionally named "nickname"). `XXX`,
    `YYY`, and `ZZZ` are optional names of images that will
    automatically be added as figures to the new entry

    Note: if you just want to do an entry to the default journal with
    no images, you can simply type `pyjournal.py` without any arguments.

  - `pyjournal.py edit [-n nickname] 'yyyy-mm-dd hh.mm.ss'`

    edit the entry corresponding to the date/time string in the journal.
    This adds a comment to the LaTeX indicating the time of the edit
    and pops up an editor window with the entry for revision.  Since the
    new changes are committed to the git repo, the history of changes to
    the entry are preserved in the git history.

    The editor to use is taken from your `EDITOR` environment variable,
	of, if that is not set, defaults to `emacs` (run in a terminal).

  - `pyjournal.py list [-n nickname] [-N N]`

    list the id (date-time) and full path to the LaTeX file for the last
    N entries.

  - `pyjournal.py build [-n nickname]`

    builds the journal PDF

  - `pyjournal.py show [-n nickname]`

    builds the journal PDF and launches the `evince` viewer in the
    background to display it.

  - `pyjournal.py status [-n nickname]`

    display the status of the journal, giving the location of hte
    files, the name of the remote version.

  - `pyjournal.py pull [-n nickname] `

    gets any changes from the master version of the journal (remote
    git bare repository)

  - `pyjournal.py push [-n nickname] `

    pushes any changes in the local journal to the remote (git bare
    repo) version


* Hashtags

  A new latex command `\htag{name}` is introduced to put a hash
  tag in the journal entry.  When you build the journal, there will
  be an index of hash tags at the end of the journal with links
  to the pages.  This can let you organize entries into topics.




* `.pyjournal` structure:

  ```
  [nickname]
  master_repo = XXX.git  ; this is what we push to/pull from
  working_path = YYY     ; local directory we interact with on our machine
  ```
