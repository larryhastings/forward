## forward

### A prototype of "forward class" / "continue class" using decorators

This is a simple prototype of my proposed `forward class` / `continue class`
syntax for Python, implemented using decorators.

The proposed syntax for Python looks like this:
```
    forward class X()

    continue class X:
        # class body goes here
        pass
```

This decorators-based version can't be quite as clean.  The equivalent
declaration using the decorators would look like this:

```
    from forward import *

    @forward()
    class X():
       ...

    @continue_(X)
    class _:
       # class body goes here
       pass
```

Specifically:

* You have to make the `forward` module available somehow.  You can just copy the
  `forward` directory into the directory you want to experiment in, or you can
  install it locally in your Python install or venv by installing the `flit`
  package from PyPI and running `flit install -s` .
* You must import and use the two decorators from the `forward` module.
  The easiest way is with `from forward import *` .
* For the `forward class` statement, you instead decorate a conventional class
  declaration with `@forward()`.  The class body should be empty, with either
  a single `pass` statement or a single ellipsis `...` on a line by itself;
  the ellipsis form is preferred.  You should name this class with the desired
  final name of your class.
* For the `continue class` statement, you instead decorate a conventional
  class declaration with `@continue_()`, passing in the forward-declared class
  object as a parameter to the decorator.  You can use the original name of
  the class if you wish, or a throwaway name like `_` as per the example.

Notes and caveats:

* To use slots, please declare them in the `forward` class.
  (If the proposed `forward class`/`continue class` syntax is added
  to Python, we'll ensure it handles slots correctly, permitting them to be
  declared in the `continue` class.)
* The `continue_` decorator returns the original "forwarded" class object.
  This permits you to stack additional decorators on the class; simply make
  sure you call the `continue_` decorator first.  (It should be on the bottom.)
* This prototype doesn't support decorators that both examine the contents of
  the class *and* return a different class, e.g. `@dataclass(slots=True)`.

#### convert/ tools

There's a cheap converter program in the `convert/` directory.  It attempts to
automatically add the `@forward()` decorator to your class definitions.  It
turns this:

```Python
    class foo(...):
        pass
```

into this:

```Python
    @forward()
    class foo(...):
        ...

    @continue_(foo)
    class _:
        pass
```

`convert/toggle_forward.py` will edit one or more Python files specified on the
command-line, making the above change.  By default it will toggle the presence of `@forward`
decorators.  You can also specify explicit behavior:

`-f` adds `@forward` decorators.
`-c` removes `@forward` decorators (changing back to *conventional class* statements).
`-t` explicitly says "toggle".

The parser is pretty dumb, so don't run it on anything precious.  If it goofs up, sorry!

`convert/apply_to_stdlib.py` takes a path to a `Lib/` directory in a CPython checkout
and recursively applies `toggle_forward.py` to nearly every Python file it finds
underneath.  It skips the `test/` tree and one silly tester file.

With a current checkout, adding `@forward()` decorators doesn't seem to break anything.
The set of tests that fails remains the same before and after adding forward decorators.

