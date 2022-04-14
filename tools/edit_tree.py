#!/usr/bin/env python3

"""
usage:
    edit_tree.py [-a|-r|-t] [-i <file> <ignore>] [-f <file>] [-d <directory>] [-m] path...

Toggles @forward() declarations in an entire tree of Python files.

Edits all Python scripts found under <path> to add/remove/toggle
use of the "forward class" proof-of-concept decorators.

Essentially, converts

    class foo(...):
        pass

into

    @forward()
    class foo(...):
        ...

    @continue_(foo)
    class _____:
        pass

By default it "toggles" the state of the files.
It detects whether the first class declared is
conventional or using forward declarations.
(Which does it see first: a line matching
"@forward()", or a line starting with "class "
or "from forward import *"?)

You can explicitly tell it what to do to the
file with a flag:

    -a add @forward() to class definitions that
       don't have it

    -r remove @forward() from class definitions
       that have it

    -t toggle the file's current behavior:
       if the file already has @forward() declarations,
       remove them, otherwise add them

When adding @forward() declarations, edit_tree.py will
also add "from forward import *" to the top of the files,
and will clean up the namespace with del statements at
the bottom of the files.

-i adds an entry to the list of things to ignore, on a
file-by-file basis.

  <file> is the path to the file, relative to path.

  if <ignore> is an integer, edit_tree.py will ignore the
  class declaration on that line of that file.

  if <ignore> is a string, edit_tree.py will ignore any class
    definition using that string as its class name in that file.
    (the list of things to ignore is only used when adding
    @forward() declarations.)

-f tells edit_tree.py to ignore a particular file in the tree.

-d tells edit_tree.py to ignore an entire subtree of directories
in the tree.

-v toggles debugging print statements.

-m toggles whether or not edit_tree.py will also install the
"forward" module in path.  by default, if behavior is "add",
and there is no "forward" module installed in path, edit_tree.py
will install a copy of the one found relative to this file
("../../forward/__init__.py").  -m toggles this behavior.
(edit_tree.py will never remove the "forward" module, even
if "behavior" is "remove".)

This program is just a hack.  It barely works well enough
to let us test the proof-of-concept against the CPython
standard library.  The parser is rudimentary:
    * It isn't smart about class statements inside
      triple-quoted strings.
    * If the class declaration line doesn't end
      with a colon, it doesn't touch it.
"""

from collections import defaultdict
import sys

import editor


def usage(s):
    sys.exit(f"error: {s}\n\n{__doc__.strip()}")

path = None
behavior = "toggle"
ignore_files = []
ignore_directories = []
ignore_file_map = defaultdict(list)
verbose = False
install_forward_module = True

process_options = True
process_directory = False
process_file = False
process_ignore = False
ignore_filename = None

for arg in sys.argv[1:]:

    if process_directory:
        ignore_directories.append(arg)
        process_directory = False
        continue

    if process_file:
        ignore_files.append(arg)
        process_file = False
        continue

    if process_ignore:
        if ignore_filename is None:
            ignore_filename = arg
            continue

        value = arg
        if value.isdigit():
            value = int(value)
        ignore_file_map[ignore_filename].append(value)
        ignore_filename = None
        process_ignore = False
        continue

    if arg.startswith("-") and process_options:
        if arg == "--":
            process_options = False
            continue
        if arg == "-v":
            verbose = not verbose
            continue
        if arg == "-m":
            install_forward_module = not install_forward_module
            continue
        if arg == "-d":
            process_directory = True
            continue
        if arg == "-f":
            process_file = True
            continue
        if arg == "-i":
            process_ignore = True
            continue

        behavior = editor.option_to_behavior(arg)
        if not behavior:
            usage("unknown option " + arg)
        continue

    path = arg
    try:
        behavior, modified_files, modified_lines = editor.forward_edit_tree(path, behavior, ignore_files, ignore_directories, dict(ignore_file_map), verbose=verbose, install_forward_module=install_forward_module)
        if verbose:
            print()
        print(f"{path}\n    {modified_files} files modified with {modified_lines} modified lines.")
    except RuntimeError as e:
        usage(str(e))

if not path:
    usage("no paths specified.")
