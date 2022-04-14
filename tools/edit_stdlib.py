#!/usr/bin/env python3

"""
usage:
    edit_stdlib.py [-a|-r|-t] [-v] <path>...

Toggles @forward() declarations in the Lib/ directory of a
CPython checkout from "git".

IMPORTANT: the CPython checkout in <path> *must* have this
*exact* revision ID checked out:

    7b87e8af0cb8df0d76e8ab18a9b12affb4526103

Any other revision is illegal and will be ignored.


Edits all Python scripts found under <path>/Lib to
add/remove/toggle use of the "forward class" proof-of-concept
decorators.


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

When adding @forward() declarations, edit_stdlib.py will
also add "from forward import *" to the top of the files,
and will clean up the namespace with del statements at
the bottom of the files.

-v toggles debugging print statements.

This program is just a hack.  It barely works well enough
to let us test the proof-of-concept against the CPython
standard library.  The parser is rudimentary:
    * It isn't smart about class statements inside
      triple-quoted strings.
    * If the class declaration line doesn't end
      with a colon, it doesn't touch it.
"""

######################################################################
######################################################################


checkout_id = "7b87e8af0cb8df0d76e8ab18a9b12affb4526103"


##
## note!
## all these paths are relative to "<cpython_root>/Lib"
## not simply "<cpython_root>"!
##

ignore_files = """

    lib2to3/tests/data/py2_test_grammar.py
    lib2to3/tests/data/crlf.py

"""

ignore_directories = """

    test

"""


ignore_file_map = """

    enum.py
        # metaclass wizardry
        Enum
        ReprEnum
        IntEnum
        StrEnum
        FlagBoundary
        Flag
        IntFlag
        EnumCheck

    re/__init__.py
        RegexFlag # enum

    re/_compiler.py
        _CompileData # slots

"""

# exceptions = [
#     # skip modifying ourselves
#     ("/forward", "__init__.py"),

#     # skip this silly EOL tester thing
#     ("/tests/data", "crlf.py"),

#     # some metaclass problem?
#     ("", "enum.py"),

#     # slots
#     ("", "weakref.py"),

#     # skip this goofy """#" nonsense, wtf
#     (None, "encodings"),

#     # skip the entire test tree (for now?)
#     (None, "test"),
#     ]


######################################################################
######################################################################


from collections import defaultdict
import os.path
import sys
import textwrap

import editor


def process_paths(s):
    """
    processes a string, line by line, as follows:

        path
        path_2

    if '#' appears in a line, the line is truncated
    to before the '#' character.
    leading and trailing whitespace is stripped.
    blank lines are ignored.


    returns a list of paths harvested from the string.
    """
    paths = []
    for line in s.strip().split("\n"):
        line, _, comment = line.partition("#")
        line = line.strip()
        if not line:
            continue
        paths.append(line)
    return paths

def process_ignore_file_map(s):
    """
    processes a string, line by line, to turn it
    into an "ignore_file_map" style dict, as follows:

        filename
           ignore1
           ignore2
        filename2
           ignore_a
           ignore_b

    first, the entire string is processed by textwrap.dedent().
    trailing whitespace is stripped from each line.
    strings at the left margin are used as keys.
    indented strings are stripped and used as values.
    (lines that are integers are turned into integers.)
    you can specify the same filename twice.
    blank lines are ignored.
    '#' works the same here as it does with process_paths().
    """
    map = defaultdict(list)
    file_path = None
    for line in textwrap.dedent(s).strip().split("\n"):
        line, _, comment = line.partition("#")
        line = line.rstrip()
        if not line:
            continue
        value = line.lstrip()
        # print(f"{line=} {value=}")
        if value == line:
            file_path = value
        else:
            assert file_path, "you must start with a file path at the left margin!"
            if value.isdigit():
                value = int(value)
            map[file_path].append(value)

    return dict(map)

ignore_files = process_paths(ignore_files)
ignore_directories = process_paths(ignore_directories)
ignore_file_map = process_ignore_file_map(ignore_file_map)

# print(f"{ignore_files=}")
# print(f"{ignore_directories=}")
# print(f"{ignore_file_map=}")
# sys.exit(0)


def usage(s):
    sys.exit(f"error: {s}\n\n{__doc__.strip()}")


path = None
behavior = "toggle"
verbose = False

process_options = True

for arg in sys.argv[1:]:

    if arg.startswith("-") and process_options:
        if arg == "--":
            process_options = False
            continue
        if arg == "-v":
            verbose = not verbose
            continue

        behavior = editor.option_to_behavior(arg)
        if not behavior:
            usage("unknown option " + arg)
        continue

    path = arg
    try:
        for subpath in process_paths("""
            Doc
            Grammar
            Lib
            LICENSE
            Python
            PCbuild
            configure
            .git
        """):
            if not os.path.exists(os.path.join(path, subpath)):
                usage(f"bad CPython checkout.  no {subpath!r} found.")
        with open(os.path.join(path, ".git", "HEAD"), "rt") as f:
            revision = f.read().strip()
        if revision != checkout_id:
            print(f"{   revision=}\n{checkout_id=}")
            usage(f"bad CPython git revision in {path!r}.\ngo to that directory and run:\n\n    git checkout {checkout_id}")
        behavior, modified_files, modified_lines = editor.forward_edit_tree(os.path.join(path, "Lib"), behavior, ignore_files, ignore_directories, ignore_file_map, verbose=verbose, install_forward_module=True)
        if verbose:
            print()
        print(f"{path}\n    {modified_files} files modified with {modified_lines} modified lines.")
    except RuntimeError as e:
        usage(str(e))

if not path:
    usage("no paths specified.")
