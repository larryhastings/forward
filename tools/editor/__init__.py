"""
The underlying Python code for editing
(adding / removing / toggling) @forward()
usage in a Python script or tree.
"""

import ast
import os.path
import re
import shutil
import sys

__all__ = []

def export(fn):
    __all__.append(fn.__name__)
    return fn



option_to_behavior_map = {
    "-a": "add",
    "-r": "remove",
    "-t": "toggle",
}

behaviors = set(option_to_behavior_map.values())

@export
def option_to_behavior(option):
    return option_to_behavior_map.get(option, None)


def is_class_definition(stripped):
    return stripped.startswith("class ") and stripped.endswith(":")

def get_indent(line, stripped):
    return line.partition(stripped)[0]

class_name_re = re.compile("^class ([_A-Za-z0-9]+)[( :]")


import_line = "from forward import *"
del_forward_line = "del forward"
del_continue__line = "del continue_"
forward_decorator_line = "@forward()"
continue_class_declaration_line = "class _____:"

ignore_sentinel_line = "# hey, forward.tools.editor! ignore this file!"

lines_to_strip = {import_line, del_forward_line, del_continue__line}


@export
def forward_edit_file(path, behavior, ignore, *, verbose=False, indent=""):
    """
    edits a Python file, either
      * adding,
      * removing, or
      * toggling the presence of
    @forward() declarations around class definitions.

    path is the file to edit.

    behavior is a string, either "add", "remove", or "toggle":
      "add" means add @forward() declarations.
      "remove" means remove @forward() declarations (change back
        to normal class definitions).
      "toggle" means detect whether or not the file already has
        @forward() declarations, and toggle that state; add them
        if the file doesn't have them, and remove them if it does
        have them.

    if behavior is "add" (or "toggle", and this was the first
    class definition encountered), it would change
        class Foo:
            a=3
    into
        @forward()
        class Foo:
            ...
        @continue_(Foo)
        class _____:
            a=3
    if behavior is "remove", it would reverse this transformation.

    forward_edit_file will also add / remove an import line
    ("from forward import *"), as well as add lines to clean
    up the namespace at the end of the file.

    ignore is an iterable of either strings or integers, only used
    when behavior is "add":
      a string indicates "don't add @forward() to a class with this name".
      an integer intdicates "ignore this line".
    (when behavior is "remove", or behavior is still "toggle",
    ignore is, itself, ignored.)

    if verbose is true, forward_edit_file will print debugging information.

    indent is a string prepended to every line printed for debugging.

    returns a tuple:
        (final_behavior, modified_lines)
    final_behavior is a behavior string indicating which behavior
    the function used.  if the requested behavior is "toggle",
    this will usually change to either "forward" or "class"
    depending on what forward_edit_file finds in the file.
    (if the file doesn't have any class declarations, this
    may remain "toggle".)

    modified_lines is the count of changed lines in the file.
    adding or removing a line counts as one modification.
    """
    if verbose:
        print(f"{indent}forward_edit_file\n{indent}  {path=}\n{indent}  {behavior=}\n{indent}  {ignore=}\n{indent}  {verbose=}")

    if behavior not in behaviors:
        behaviors_str = ', '.join(repr(x) for x in behaviors)
        raise RuntimeError(f"behavior {behavior!r} not in {behaviors_str}")

    if not (path.endswith(".py") and os.path.exists(path)):
        raise RuntimeError(f"invalid Python file {path!r}")

    invalid_ignore_values = [o for o in ignore if not isinstance(o, (int, str))]
    if invalid_ignore_values:
        raise RuntimeError(f"invalid values in ignore: {invalid_ignore_values}")

    lines = []
    modified_lines = 0

    ignore_line_numbers = {o for o in ignore if isinstance(o, int)}
    ignore_classnames = {o for o in ignore if isinstance(o, str)}

    if behavior == "toggle":
        state = "detect"
    else:
        state = "initial"

    with open(path, "rt", encoding="utf-8") as f:
        stat = os.stat(f.fileno())
        times_ns = stat.st_atime_ns, stat.st_mtime_ns
        text = f.read()

    for line_number, line in enumerate(text.splitlines(), 1):
        original = line.rstrip('\n')
        line = line.rstrip()
        stripped = line.lstrip()

        if not stripped:
            lines.append(original)
            continue

        if line == ignore_sentinel_line:
            return behavior, 0

        if state == "detect":
            if stripped.startswith("class "):
                behavior = "add"
                # intentional fall-through

            elif stripped == import_line:
                behavior = "remove"
                # don't keep the import line
                # (which is therefore a modification)
                modified_lines += 1
                continue

            elif stripped == forward_decorator_line:
                behavior = "remove"
                # fall through so we change state correctly

            if behavior == "toggle":
                lines.append(original)
                continue

            state = "initial"
            # intentional fall-through

        if state == "initial":
            if behavior == "remove":
                if stripped == forward_decorator_line:
                    state = "emit class declaration"
                    modified_lines += 1
                elif stripped not in lines_to_strip:
                    lines.append(original)
                else:
                    modified_lines += 1
                continue

            assert behavior == "add"

            if line_number in ignore_line_numbers:
                lines.append(line)
                continue

            if stripped == forward_decorator_line:
                # this file already has forward declarations!
                return behavior, 0

            if is_class_definition(stripped):
                code_indent = get_indent(line, stripped)
                match = class_name_re.match(stripped)
                if not match:
                    # I give up, probably a comment.
                    lines.append(original)
                    continue
                classname = match.group(1)
                if classname in ignore_classnames:
                    lines.append(original)
                    continue

                lines.append(code_indent + forward_decorator_line)
                lines.append(original)
                lines.append(code_indent + f"    ...")
                lines.append(code_indent + f"@continue_({classname})")
                lines.append(code_indent + continue_class_declaration_line)
                modified_lines += 4
                continue
            lines.append(original)
            continue

        if state == "emit class declaration":
            # intentionally fragile
            # only understands its own style
            # @forward() must be followed by class definition
            assert is_class_definition(stripped), "didn't find class definition when we expected it, file " + repr(path) + " line " + repr(line)
            lines.append(original)
            state = "looking for class declaration"
            continue

        if state == "looking for class declaration":
            if stripped == continue_class_declaration_line:
                state = "initial"
            modified_lines += 1
            continue

        if state == "flush next class declaration":
            lines.append(original)
            if is_class_definition(stripped):
                state = "initial"
            continue

        raise RuntimeError(f"unhandled line {line!r}, current state {state!r}")

    if not lines:
        return behavior, 0

    if modified_lines:
        if behavior == "add":
            tree = compile(text, path, 'exec', ast.PyCF_ALLOW_TOP_LEVEL_AWAIT | ast.PyCF_ONLY_AST, dont_inherit=True)

            for i, node in enumerate(tree.body):
                if (i == 0) and isinstance(node, ast.Expr) and isinstance(node.value.value, str):
                    continue
                break

            first_line = node.lineno
            # AST line numbers start with 1!
            # lines is 0-indexed.
            assert first_line > 0
            first_line -= 1

            lines.insert(first_line, import_line)
            lines.append("")
            lines.append(del_forward_line)
            lines.append(del_continue__line)
            lines.append("")
            modified_lines += 5
        else:
            # we already removed the "del forward" and "del continue_" lines.
            # let's also strip the two blank lines we inserted.
            for _ in range(2):
                if not lines[-1]:
                    lines.pop()
                    modified_lines += 1

    text = "\n".join(lines) + "\n"

    output_path = path
    with open(output_path, "wt") as f:
        f.write(text)
    os.utime(output_path, ns=times_ns)
    if verbose:
        print(f"{indent}  returning {behavior=}, {modified_lines=}")
    return behavior, modified_lines


@export
def forward_edit_tree(path, behavior, ignore_files, ignore_directories, ignore_file_map, *, verbose=False, install_forward_module=True):
    """
    Applies forward_edit_file to all the "*.py" files found under path.

    behavior is the same as the argument to forward_edit_file().

    ignore_files is a list of files relative to "path" that will simply
    be ignored.

    ignore_directories is a list of directories relative to "path" that
    will simply be ignored.

    ignore_file_map is a map of file paths to "ignore" lists.  the "ignore"
    list is the "ignore" argument passed in to forward_edit_file.  the file
    path is relative to the "path" argument.

    note that you should always use "/" as the path separator for
    ignore_directories, ignore_files, and ignore_file_map, even on Windows.
    ("/" works fine as a directory separator on Windows, and being consistent
    in this way made writing the tools easier.)

    if verbose is true, forward_edit_tree will print debugging information.

    if install_forward_module is true, and behavior is "add", forward_edit_tree
    will also install the "forward" module ("../../forward") in the root of path
    if there isn't already one there.  (forward_edit_tree doesn't remove this
    "forward" module, even if behavior is "remove".)

    note also that "toggle" behavior is detected once, and that behavior is
    kept for the rest of processing.  (if you pass in behavior="toggle", it
    doesn't simply pass in "toggle" for every file; it passes in the behavior
    returned by forward_edit_file() for the file.)

    returns a tuple:
        (final_behavior, modified_files, modified_lines)
    final_behavior and modified_lines are the same as returned from
    forward_edit_file, although modified_lines is cumulative over all files.

    modified_files is the count of files modified.
    """

    if verbose:
        print(f"forward_edit_tree\n  {path=}\n  {behavior=}\n  {ignore_files=}\n  {ignore_directories=}\n  {ignore_file_map=}\n  {verbose=}\n  {install_forward_module=}")

    modified_files = 0
    modified_lines = 0

    # huge speedup time! holy moly!
    if not isinstance(ignore_directories, set):
        ignore_directories = set(ignore_directories)
    if not isinstance(ignore_files, set):
        ignore_files = set(ignore_files)

    if install_forward_module:
        editor_module = sys.modules['editor']
        editor_module_path = editor_module.__file__.replace("\\", "/")
        assert editor_module_path.endswith("/forward/tools/editor/__init__.py")
        forward_root = editor_module_path.partition("/tools/editor/__init__.py")[0]
        forward_module_path = os.path.join(forward_root, "forward", "__init__.py")

        output_module_path = os.path.join(path, "forward", "__init__.py")
        if not os.path.isfile(output_module_path):
            output_module_dir = os.path.dirname(output_module_path)
            if not os.path.isdir(output_module_dir):
                os.mkdir(output_module_dir)
            shutil.copy2(forward_module_path, output_module_path)
            modified_files += 1

    for (dirpath, dirnames, filenames) in os.walk(path):

        if verbose:
            print()
            print(f"  {dirpath=}")

        assert dirpath.startswith(path)
        relative_dir = os.path.relpath(dirpath, path)
        if relative_dir in ignore_directories:
            if verbose:
                print(f"      ignoring (was found in ignore_directories)")
            dirnames.clear()
            continue

        if verbose:
            print(f"  {dirnames=}")
            print(f"  {filenames=}")

        for filename in filenames:
            if not (filename and filename.endswith(".py")):
                continue
            relative_path = os.path.join(relative_dir, filename)
            if verbose:
                print()
                print(f"  {relative_path=}")
            if relative_path in ignore_files:
                if verbose:
                    print(f"    ignoring (was found in ignore_files)")
                continue

            ignore = ignore_file_map.get(relative_path, ())

            file_path = os.path.join(dirpath, filename)
            try:
                behavior, file_modified_lines = forward_edit_file(file_path, behavior, ignore, verbose=verbose, indent="    ")
            except UnicodeDecodeError:
                # just ignore files we couldn't understand
                continue
            if file_modified_lines:
                modified_files += 1
                modified_lines += file_modified_lines

    if verbose:
        print(f"  returning {behavior=}, {modified_files=}, {modified_lines=}")

    return (behavior, modified_files, modified_lines)
