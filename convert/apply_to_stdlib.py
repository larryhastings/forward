#!/usr/bin/env python3

exceptions = [
    # skip modifying ourselves
    ("/forward", "__init__.py"),

    # skip this silly EOL tester thing
    ("/tests/data", "crlf.py"),

    # skip the entire test tree (for now?)
    (None, "test"),
    ]

import os.path
import subprocess
import sys

def usage(s):
    sys.exit("Error: " + s + "\n\nnusage: " + sys.argv[0] + " <path>\n\nRuns convert.py on (nearly) all .py files found under <path>.")


flag = "-t"
flag_set = False
path = None
for arg in sys.argv[1:]:
    if arg.startswith("-"):
        if flag_set:
            usage("you can only specify one flag")
        if arg not in ("-c", "-f", "-t"):
            usage("invalid option: " + arg)
        flag = arg
        flag_set = True
        continue
    path = arg
    break

if not path:
    usage("no path specified.")

if not os.path.isdir(path):
    usage("invalid path specified.")


paths = []
processed_count = 0

for (dirpath, dirnames, filenames) in os.walk(path):

    for exc_dirpath_suffix, exc_filename in exceptions:
        if (not exc_dirpath_suffix) and (exc_filename in dirnames):
            # print("skip the", exc_filename, f"tree in {dirpath}.")
            dirnames.remove(exc_filename)

    for filename in filenames:
        if not filename.endswith(".py"):
            continue
        for exc_dirpath_suffix, exc_filename in exceptions:
            if exc_dirpath_suffix and dirpath.endswith(exc_dirpath_suffix) and filename == exc_filename:
                filename = None
                break
        if not filename:
            continue
        path = os.path.join(dirpath, filename)
        paths.append(path)
        processed_count += 1

        if len(paths) >= 20:
            cmdline = [sys.executable, "toggle_forward.py", flag]
            cmdline.extend(paths)
            # print(cmdline)
            subprocess.run(cmdline)
            paths.clear()

print(f"{processed_count} files processed.\nBe sure to copy the 'forward' directory into:\n    {path!r}")