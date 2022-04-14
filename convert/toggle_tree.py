#!/usr/bin/env python3

__doc__ = """

usage: toggle_tree.py [-t|-f|-c] tree_root...

Toggles @forward() declarations in an entire tree of Python files.


options:
-t            toggle @forward() declarations in each file
-f            explicitly add @forward() declarations to each file
-c            explicitly remove @forward() declarations from each file
              (return the file to using normal _c_lass declarations)
-d dir        ignore this relative subdir (and all files underneath it)
-p path       ignore this relative file path
-i path cls   ignore this classname in this relative file path

"""

import os.path
import sys

from toggle_file import edit_forward_path, option_to_behavior

argv0 = os.path.abspath(sys.argv[0])
convert_dir = os.path.dirname(argv0)
root_dir, _ = os.path.split(convert_dir)
forward_module_dir = os.path.join(root_dir, "forward")
assert (_ == "convert") and os.path.isdir(forward_module_dir), "apply_to_tree not run from 'forward' checkout!"

forward_module_path = os.path.join(forward_module_dir, "__init__.py")

exceptions = [
    # skip modifying ourselves
    ("/forward", "__init__.py"),

    # skip this silly EOL tester thing
    ("/tests/data", "crlf.py"),

    # some metaclass problem?
    ("", "enum.py"),

    # slots
    ("", "weakref.py"),

    # skip this goofy """#" nonsense, wtf
    (None, "encodings"),

    # skip the entire test tree (for now?)
    (None, "test"),
    ]


def edit_forward_tree(root, behavior, ignore_dirs, ignore_files, ignore_map, *, verbose=0):
    if verbose:
        print(f"edit_forward_tree:\n  {root=}\n  {behavior=}\n  {ignore_dirs=}\n  {ignore_files=}\n  {ignore_map=}\n  {verbose=}")
    modifications = 0
    modified_files = 0

    # copy over forward/__init__.py
    # but only if they don't already have one.
    output_module_path = os.path.join(root, "forward", "__init__.py")
    if not os.path.isfile(output_module_path):
        output_module_dir = os.path.dirname(output_module_path)
        if not os.path.isdir(output_module_dir):
            os.mkdir(output_module_dir)
        shutil.copy2(forward_module_path, output_module_path)
        modified_files += 1

    for (dirpath, dirnames, filenames) in os.walk(root):

        assert dirpath.startswith(root)
        relative_dir = os.path.relpath(dirpath, root)
        if relative_dir in ignore_dirs:
            dirnames.empty()
            continue

        for filename in filenames:
            if not (filename and filename.endswith(".py")):
                continue
            if filename in ignore_files:
                continue

            relative_path = os.path.join(relative_dir, filename)
            ignore = ignore_map.get(relative_path, ())

            file_path = os.path.join(dirpath, filename)
            file_behavior, _modifications = edit_forward_path(file_path, behavior, ignore, verbose=verbose)
            if _modifications:
                modified_files += 1
                modifications += _modifications

    return (modified_files, modifications)

if __name__ == "__main__":

    def usage(s):
        sys.exit("error: " + s + "\n\n" + __doc__.strip())

    behavior = "toggle"
    paths = 0

    ignore_dirs = set()
    ignore_dirs_add = False
    ignore_files = set()
    ignore_files_add = False
    ignore_map = {}
    ignore_map_args = 0
    last_option = None
    verbose = 0

    for arg in sys.argv[1:]:
        if ignore_dirs_add:
            ignore_dirs.add(arg)
            continue
        if ignore_files_add:
            ignore_files.add(arg)
            continue
        if ignore_map_args == 2:
            ingore_map_key = arg
            ignore_map_args -= 1
            continue
        if ignore_map_args == 1:
            value = arg
            s = ignore_map.get(ingore_map_key, None)
            if s is None:
                s = set()
                ignore_map[ingore_map_key] = s
            s.add(value)
            ignore_map_args = 0
            continue
        if arg.startswith("-"):
            if arg == "-d":
                ignore_dirs_add = True
                last_option = arg
                continue
            if arg == "-p":
                ignore_files_add = True
                last_option = arg
                continue
            if arg == "-m":
                ignore_map = 2
                last_option = arg
                continue
            if arg == "-v":
                verbose += 1
                continue
            behavior = option_to_behavior.get(arg)
            if behavior is None:
                usage(f"unknown option {arg!r}")
            continue

        path = arg

        if not os.path.isdir(path):
            usage("invalid path specified")
        modified_files, modifications = edit_forward_tree(path, behavior, ignore_dirs, ignore_files, ignore_map, verbose=verbose)
        paths += 1
        print(f"{path}\n    {modified_files} files modified with {modifications} modifications.")

    if ignore_dirs_add or ignore_files_add or ignore_map_args:
        usage(f"incomplete use of option {last_option}")

    if not paths:
        usage("no path specified")
