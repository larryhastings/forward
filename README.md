## Forward

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

* You have to make the module available.  You can just copy the `forward`
  directory into the directory you want to work in, or you can install it
  locally by installing the `flit` package from PyPI and running `flit install -s` .
* You must import and use the two decorators from the `forward` module.
  The easiest way is to use `from forward import *` .
* For the `forward class` statement, you instead decorate a conventional class
  declaration with `@forward()`.  The class body should be empty, with either
  a single `pass` statement or a single ellipsis `...` on a line by itself;
  the ellipsis form is preferred.
* For the `continue class` statement, you instead decorate a conventional
  class declaration with `@continue_()`, passing in the forward-declared class
  object as a parameter to the decorator.  The class you're decorating is
  thrown away (the `continue_` decorator returns `None`), so its name should
  be an unused variable; the class name `_` is preferred.