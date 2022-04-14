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
        Enum
        ReprEnum
        IntEnum
        StrEnum
        FlagBoundary
        Flag
        IntFlag
        EnumCheck

"""

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

    leading and trailing whitespace is stripped.
    blank lines and lines starting with # are ignored.

    returns a list of paths harvested from the string.
    """
    paths = []
    for line in s.strip().split("\n"):
        line = line.strip()
        if (not line) or line.startswith("#"):
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
    blank lines and lines starting with # are ignored.
    """
    map = defaultdict(list)
    file_path = None
    for line in textwrap.dedent(s.strip()).split("\n"):
        line = line.rstrip()
        if (not line) or line.startswith("#"):
            continue
        value = line.lstrip()
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













######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################



# #!/usr/bin/env python3

# __doc__ = """

# usage: toggle_tree.py [-t|-f|-c] tree_root...

# Toggles @forward() declarations in an entire tree of Python files.


# options:
# -t            toggle @forward() declarations in each file
# -f            explicitly add @forward() declarations to each file
# -c            explicitly remove @forward() declarations from each file
#               (return the file to using normal _c_lass declarations)
# -d dir        ignore this relative subdir (and all files underneath it)
# -p path       ignore this relative file path
# -i path cls   ignore this classname in this relative file path

# """

# import os.path
# import sys

# from toggle_file import edit_forward_path, option_to_behavior

# argv0 = os.path.abspath(sys.argv[0])
# convert_dir = os.path.dirname(argv0)
# root_dir, _ = os.path.split(convert_dir)
# forward_module_dir = os.path.join(root_dir, "forward")
# assert (_ == "convert") and os.path.isdir(forward_module_dir), "apply_to_tree not run from 'forward' checkout!"

# forward_module_path = os.path.join(forward_module_dir, "__init__.py")

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


# def edit_forward_tree(root, behavior, ignore_dirs, ignore_files, ignore_map, *, verbose=0):
#     if verbose:
#         print(f"edit_forward_tree:\n  {root=}\n  {behavior=}\n  {ignore_dirs=}\n  {ignore_files=}\n  {ignore_map=}\n  {verbose=}")
#     modifications = 0
#     modified_files = 0

#     # copy over forward/__init__.py
#     # but only if they don't already have one.
#     output_module_path = os.path.join(root, "forward", "__init__.py")
#     if not os.path.isfile(output_module_path):
#         output_module_dir = os.path.dirname(output_module_path)
#         if not os.path.isdir(output_module_dir):
#             os.mkdir(output_module_dir)
#         shutil.copy2(forward_module_path, output_module_path)
#         modified_files += 1

#     for (dirpath, dirnames, filenames) in os.walk(root):

#         assert dirpath.startswith(root)
#         relative_dir = os.path.relpath(dirpath, root)
#         if relative_dir in ignore_dirs:
#             dirnames.empty()
#             continue

#         for filename in filenames:
#             if not (filename and filename.endswith(".py")):
#                 continue
#             if filename in ignore_files:
#                 continue

#             relative_path = os.path.join(relative_dir, filename)
#             ignore = ignore_map.get(relative_path, ())

#             file_path = os.path.join(dirpath, filename)
#             file_behavior, _modifications = edit_forward_path(file_path, behavior, ignore, verbose=verbose)
#             if _modifications:
#                 modified_files += 1
#                 modifications += _modifications

#     return (modified_files, modifications)

# if __name__ == "__main__":

#     def usage(s):
#         sys.exit("error: " + s + "\n\n" + __doc__.strip())

#     behavior = "toggle"
#     paths = 0

#     ignore_dirs = set()
#     ignore_dirs_add = False
#     ignore_files = set()
#     ignore_files_add = False
#     ignore_map = {}
#     ignore_map_args = 0
#     last_option = None
#     verbose = 0

#     for arg in sys.argv[1:]:
#         if ignore_dirs_add:
#             ignore_dirs.add(arg)
#             continue
#         if ignore_files_add:
#             ignore_files.add(arg)
#             continue
#         if ignore_map_args == 2:
#             ingore_map_key = arg
#             ignore_map_args -= 1
#             continue
#         if ignore_map_args == 1:
#             value = arg
#             s = ignore_map.get(ingore_map_key, None)
#             if s is None:
#                 s = set()
#                 ignore_map[ingore_map_key] = s
#             s.add(value)
#             ignore_map_args = 0
#             continue
#         if arg.startswith("-"):
#             if arg == "-d":
#                 ignore_dirs_add = True
#                 last_option = arg
#                 continue
#             if arg == "-p":
#                 ignore_files_add = True
#                 last_option = arg
#                 continue
#             if arg == "-m":
#                 ignore_map = 2
#                 last_option = arg
#                 continue
#             if arg == "-v":
#                 verbose += 1
#                 continue
#             behavior = option_to_behavior.get(arg)
#             if behavior is None:
#                 usage(f"unknown option {arg!r}")
#             continue

#         path = arg

#         if not os.path.isdir(path):
#             usage("invalid path specified")
#         modified_files, modifications = edit_forward_tree(path, behavior, ignore_dirs, ignore_files, ignore_map, verbose=verbose)
#         paths += 1
#         print(f"{path}\n    {modified_files} files modified with {modifications} modifications.")

#     if ignore_dirs_add or ignore_files_add or ignore_map_args:
#         usage(f"incomplete use of option {last_option}")

#     if not paths:
#         usage("no path specified")



# line_prefixes_we_hate = [
#     "@dataclass(slots=True)",
#     "@enum.global_enum",
#     "@enum._simple_enum",
#     "@global_enum",
#     "@_simple_enum",
#     "__slots__ = ",
#     ]




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

# import os.path
# import subprocess
# import sys

# def usage(s):
#     sys.exit("Error: " + s + "\n\nnusage: " + sys.argv[0] + " <path>\n\nRuns convert.py on (nearly) all .py files found under <path>.")


# flag = "-t"
# flag_set = False
# path = None
# for arg in sys.argv[1:]:
#     if arg.startswith("-"):
#         if flag_set:
#             usage("you can only specify one flag")
#         if arg not in ("-c", "-f", "-t"):
#             usage("invalid option: " + arg)
#         flag = arg
#         flag_set = True
#         continue
#     path = arg
#     break

# if not path:
#     usage("no path specified.")

# if not os.path.isdir(path):
#     usage("invalid path specified.")


# paths = []
# processed_count = 0

# for (dirpath, dirnames, filenames) in os.walk(path):

#     for exc_dirpath_suffix, exc_filename in exceptions:
#         if (exc_dirpath_suffix is None) and (exc_filename in dirnames):
#             # print("skip the", exc_filename, f"tree in {dirpath}.")
#             dirnames.remove(exc_filename)

#     for filename in filenames:
#         if not filename.endswith(".py"):
#             continue
#         for exc_dirpath_suffix, exc_filename in exceptions:
#             if ((exc_dirpath_suffix is not None)
#                 and dirpath.endswith(exc_dirpath_suffix)
#                 and (filename == exc_filename)):
#                 filename = None
#                 break
#         if not filename:
#             continue
#         file_path = os.path.join(dirpath, filename)
#         paths.append(file_path)
#         processed_count += 1

#         if len(paths) >= 20:
#             cmdline = [sys.executable, "toggle_forward.py", flag]
#             cmdline.extend(paths)
#             # print(cmdline)
#             subprocess.run(cmdline)
#             paths.clear()

# print(f"{processed_count} files processed.\nBe sure to copy the 'forward' directory into:\n    {path!r}")