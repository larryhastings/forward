## forward

### A proof-of-concept of "forward class" / "continue class" using decorators

This is a simple proof-of-concept of my proposed `forward class` / `continue class`
syntax for Python, implemented using decorators.

#### The proposed syntax for Python

The proposed syntax for Python is as follows.  Today, a single statement both
declares and defines a class, the `class` statement:

```
    class X():
        # class body goes here
        pass
```

This syntax would allow you to break that into two separate statements.
The first statement is `forward class`, which declares the class.
The second statement is `continue class`, which defines the contents
of the class.  If we change the previous code example to use these new
statements, it'd read as follows:

```
    forward class X()

    continue class X:
        # class body goes here
        pass
```

The bases and metaclass must be declared with the `forward class` statement;
the class body of course goes with the `continue class` statement.

Note that the `X` in `continue class X` is not a *name*, it is
an *expression*.  This version also works:

```
    forward class X()
    snodgrass = X

    continue class snodgrass:
        # class body goes here
        pass
```

I like to think of the syntax as cutting the declaration and the definition
apart, between the end of the parentheses and before the colon:

```
                 +------8X-- snip snip snip!
       class X() | :
  -8X------------+
          # class body goes here
          pass
```

#### Semantics of "forward class" objects

`forward class X` declares a class, but the class is explicitly
not fully declared yet.  So how does this object behave?

The "consenting adults" rule suggests that the forward-declared
class object must permit most operations.  You should be able to
examine the object, compare it to other objects, inspect some
attributes (`__name__`, `__mro__`, `__class__`), and even set
attributes.

However, the user isn't permitted to instantiate a forward-declared
class object until after the corresponding `continue class X`.
The best way to ensure this seems to be to add a new dunder
attribute, `__forward__`, which if present tells the Python
runtime that this is a forward-declared but incomplete class.
The `continue class` statement would strip this flag from the
object, after which it could be instantiated.

It is explicitly permissible to declare a `forward class` without
ever completing the class with `continue class`.  If all you
need is an object that represents the class--say, to satisfy
static type annotation use cases--a forward-declared class object
should work fine.  (This meshes )

Both the `forward class` and `continue class` statements
support decorators, and the user may use decorators with either
or both statements for the same class.  Of course, now that we
are splitting the responsibilities of the `class` statement
between two new statements, which decorator goes with which
statement becomes a new concern.  In general, decorators that
don't examine the contents of the class, but simply want to
register the class object and its name, can decorate the
`forward class` statement, and all decorators that meaningfully
examine the contents of the class should decorate the
`continue class` statement.

This leads us to one known use case where a decorator that
works with conventionally-declared classes *cannot* work properly
with either `forward class` *or* `continue class`: a decorator
that subclasses the class it's decorating, and returns that
subclass, and *also* must meaningfully examine the declared
contents of that class.  An example of a decorator that does
this is the new 3.10 feature `@dataclass(slots=True)`.

(We also have an idea to ameliorate this specific situation.
Right now, a class that uses `__slots__` must define it
in the class body; it cannot be usefully inserted after the
class is defined.  If we could make that late-binding, so that
`__slots__` could be set any time before the class is first
*instantiated,* `@dataclass(slots=True` wouldn't need to
subclass the class, and would work fine when decorating a
`continue class` statement.)

One final note.  Why must the base and metaclass be declared
with the `forward class` statement?  The point of this new
syntax is to allow creating the real class object, permitting
users of the class to take references to it early, before it's
fully defined.  And the class could be declared with a
metaclass, and the metaclass could have a `__new__`, which
means it's responsible for creating the class object, and
this syntax would have to preserve that behavior.

#### forward classes and PEP 649

I suggest that `forward class` meshes nicely with PEP 649.

PEP 649 solves the forward-reference and circular-reference
problem for a lot of use cases, but not all.  So by itself
it's not quite a complete solution to the problem.

This `forward class` proposal seems like it should solve all
the forward-reference and circular-reference problems faced
by Python users today.  However, its use requires
backwards-incompatible code changes.

By adding both PEP 649 and `forward class` to Python, we
would get the best of both worlds.  PEP 649 would handle the
forward-reference and circular-reference problems most of
the time, but the user could resort to `forward class`
for the really stubborn edge cases that PEP 649 can't handle.


### This proof-of-concept using decorators

This repo contains a proof-of-concept of the `forward class` /
`continue class` syntax, implemented using decorators.
And, considering all that, it works surprisingly well!
But naturally the syntax using this decorators-based version
can't be quite as clean.  The equivalent declaration for
`class X` using these decorators would be as follows:

```Python
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
* You may use additional decorators with either or both of these decorators.
  However it's vital that `@forward()` and `@continue_()` are the
  *first* decorators run--that is, they should be on the *bottom* of the
  stack of decorators.

Notes and caveats:

* To use `__slots__`, please declare them in the `forward` class.
  (If the proposed `forward class`/`continue class` syntax is added
  to Python, we'll ensure it handles slots correctly, permitting them to be
  declared in the `continue` class.)
* The `continue_` decorator returns the original "forwarded" class object.
  This is what permits you to stack additional decorators on the class.
  (But again, you must call the `continue_` decorator first--it should be
  on the bottom.)
* Like the proposed syntax, this proof-of-concept doesn't support decorators that
  both examine the contents of the class *and* return a different class,
  e.g. `@dataclass(slots=True)` in Python 3.10.


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

