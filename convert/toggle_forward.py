#!/usr/bin/env python3

__doc__ = """
usage: toggle_forward.py [-c|-f|-t] <python_script>...

Converts a Python script found at <python_script>
to use the "forward class" prototype, or converts
it back to conventional "class" declarations.

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

It can also reverse this transformation.

By default it "toggles" the state of the file.
It detects whether the first class declared is
conventional or using forward declarations.
(Which does it see first, a line matching
"@forward()", or a line starting with "class "?)

You can explicitly tell it what to do to the
file with a flag:
    -f add @forward() to class definitions that
       don't have it
    -c remove @forward() from class definitions
       that have it
    -t detect and toggle the current behavior

This program is just a hack so we can test forward
against the Python standard library.
The parser is rudimentary:
    * It isn't smart about class statements inside
      triple-quoted strings.
    * If the class declaration line doesn't end
      with a colon, it doesn't touch it.

"""

import os
import re
import sys

argv = sys.argv[1:]

behavior = "toggle"

found_a_file = False


def usage(s):
    sys.exit(s + "\n\n" + __doc__.strip())

def is_class_definition(stripped):
    return stripped.startswith("class ") and stripped.endswith(":")

def get_indent(line, stripped):
    return line.partition(stripped)[0]

line_prefixes_we_hate = [
    "@dataclass(slots=True)",
    "@enum.global_enum",
    "@enum._simple_enum",
    "@global_enum",
    "@_simple_enum",
    "__slots__ = ",
    ]


import_line = "from forward import *"
del_forward_line = "del forward"
del_continue__line = "del continue_"

lines_to_strip = {import_line, del_forward_line, del_continue__line}

class_name_re = re.compile("^class ([_A-Za-z0-9]+)[( :]")

for arg in argv:
    if arg.startswith("-"):
        if arg == "-f":
            behavior = "forward"
        elif arg == "-c":
            behavior = "class"
        elif arg == "-t":
            behavior = "toggle"
        else:
            usage("unknown flag " + arg)
        continue
    path = arg
    if not (path.endswith(".py") and os.path.exists(path)):
        usage("invalid Python file " + repr(path))

    if behavior == "toggle":
        add_forward = None
        state = "detect"
    else:
        add_forward = behavior == "forward"
        state = "initial"

    lines = []
    aborted = False
    def abort():
        global aborted
        aborted = True
        lines.clear()

    indent = None

    with open(path, "rt", encoding="utf-8") as f:
        stat = os.stat(f.fileno())

        times = stat.st_atime_ns, stat.st_mtime_ns
        found_a_file = True
        modified = False

        for line in f:
            if aborted:
                break
            original = line.rstrip('\n')
            line = line.rstrip()
            stripped = line.lstrip()
            # print(f"[{state:20}] {stripped}")
            if not stripped:
                lines.append(original)
                continue

            for prefix in line_prefixes_we_hate:
                if stripped.startswith(prefix):
                    abort()
                    break
            if aborted:
                break

            if state == "detect":
                if stripped.startswith("class "):
                    add_forward = True

                elif stripped == import_line:
                    add_forward = False
                    # throw away the import line
                    continue

                if add_forward is None:
                    lines.append(original)
                    continue

                state = "initial"
                # intentional fall-through

            if state == "initial":
                if not add_forward:
                    if stripped == "@forward()":
                        state = "emit class declaration"
                    elif stripped not in lines_to_strip:
                        lines.append(original)
                    else:
                        modified = True
                    continue
                else:
                    if stripped == "@forward()":
                        # this file already has forward declarations!
                        abort()
                        break

                    if is_class_definition(stripped):
                        indent = get_indent(line, stripped)
                        match = class_name_re.match(stripped)
                        if not match:
                            # I give up, probably a comment.
                            lines.append(original)
                            continue
                        classname = match.group(1)
                        lines.append(indent + f"@forward()")
                        lines.append(original)
                        lines.append(indent + f"    ...")
                        lines.append(indent + f"@continue_({classname})")
                        lines.append(indent + f"class _____:")
                        modified = True
                        continue
                    lines.append(original)
                    continue

            if state == "emit class declaration":
                # intentionally fragile
                # only understands its own style
                # @forward() must be followed by class definition
                assert is_class_definition(stripped), "didn't find class definition when we expected it, file " + repr(path) + " line " + repr(line)
                lines.append(original)
                state = "looking for class _____"
                continue

            if state == "looking for class _____":
                if stripped == "class _____:":
                    state = "initial"
                else:
                    modified = True
                continue

    if not lines:
        continue

    if modified:
        if add_forward:
            # insert import line
            line_no = 0
            if lines[0].startswith("#!"):
                line_no = 1
            double_quotes = ('"""', "'''")
            if lines[line_no].strip().startswith(double_quotes):
                marker = lines[line_no].strip()[:3]
                # detect """ foo """
                if not lines[line_no].partition(marker)[2].strip():
                    line_no += 1
                while line_no < len(lines):
                    if lines[line_no].strip().endswith(marker):
                        line_no += 1
                        break
                    line_no += 1
                    continue

            lines.insert(line_no, import_line)
            lines.append("")
            lines.append(del_forward_line)
            lines.append(del_continue__line)
            lines.append("")
        else:
            # stripping two trailing blank lines, because we added two.
            for _ in range(2):
                if not lines[-1]:
                    lines.pop()

    text = "\n".join(lines) + "\n"
    # output_path = path + ".txt"
    output_path = path
    with open(output_path, "wt") as f:
        f.write(text)
    os.utime(output_path, ns=times)

if not found_a_file:
    usage("no files specified.")
