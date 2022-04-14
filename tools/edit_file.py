#!/usr/bin/env python3

"""
usage:
    edit_file.py [-a|-r|-t] [-i <ignore>] [-v] <python_script>...

Edits the Python script found at <python_script>
to add/remove/toggle use of the "forward class"
proof-of-concept decorators.

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

By default it "toggles" the state of the file.
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

When adding @forward() declarations, edit_file.py will
also add "from forward import *" to the top of the file,
and will clean up the namespace with del statements at
the bottom of the file.

-i adds an entry to the list of things to ignore.

  if <ignore> is an integer, edit_file.py will ignore the
  class declaration on that line.

  if <ignore> is a string, edit_file.py will ignore any class
    definition using that string as its class name.
    (the list of things to ignore is only used when adding
    @forward() declarations.)

-v toggles debugging print statements.

This program is just a hack.  It barely works well enough
to let us test the proof-of-concept against the CPython
standard library.  The parser is rudimentary:
    * It isn't smart about class statements inside
      triple-quoted strings.
    * If the class declaration line doesn't end
      with a colon, it doesn't touch it.

"""

import os.path
import re
import sys

import editor


def usage(s):
    sys.exit(f"error: {s}\n{__doc__.strip()}")


path = None
behavior = "toggle"
ignore = []
verbose = False

process_options = True
process_ignore = False

for arg in sys.argv[1:]:

    if process_ignore:
        value = arg
        if value.isdigit():
            value = int(value)
        ignore.append(value)
        process_ignore = False
        continue

    if arg.startswith("-") and process_options:
        if arg == "--":
            process_options = False
            continue
        if arg == "-v":
            verbose = not verbose
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
        behavior, modified_lines = editor.forward_edit_file(path, behavior, ignore, verbose=verbose)
        if verbose:
            print()
        print(f"{path}\n")
        if modified_lines:
            print(f"    modified with {modified_lines} modifications.")
        else:
            print(f"    not modified.")
    except RuntimeError as e:
        usage(str(e))
    except UnicodeDecodeError:
        raise RuntimeError(f"could not decode file {path!r}")

if process_ignore:
    usage("missing argument to -i")

if not path:
    usage("no files specified")
