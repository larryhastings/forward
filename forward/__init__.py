# Demo of "forward" prototype by Larry Hastings, March 2022.
# This software is placed in the public domain or under the CC0-1.0-Universal license, whichever is more permissive.
"""
Prototype of "forward class" / "continue class", using decorators.
"""

__version__ = "1.0"

class _sample_class:
    pass

class _sample_class_with_bases_and_metaclass(_sample_class, metaclass=type):
    pass

dont_overwrite_attributes = {"__module__",}
existing_attributes = set(_sample_class.__dict__) | set(_sample_class_with_bases_and_metaclass.__dict__)

object_init = object.__init__

def forward():
    def forward(cls):
        cls.__forward__ = True
        message = f"{cls.__name__} is a forward-declared class"
        def __init__(self, *a, **kw):
            raise TypeError(message)
        cls.__forward_new_init__ =  cls.__init__ = __init__
        return cls
    return forward

def continue_(forward_cls):
    if ((not isinstance(forward_cls, type))
        or (not hasattr(forward_cls, '__forward__'))
        or not forward_cls.__forward__):
        raise TypeError(f"{forward_cls.__name__} is not a forward-declared class")

    def continue_(continue_cls):
        if not isinstance(continue_cls, type):
            raise TypeError(f"{continue_cls.__name__} is not a class")
        if hasattr(continue_cls, '__forward__') and continue_cls.__forward__:
            raise TypeError(f"{continue_cls.__name__} must not be a forward-declared class")

        del forward_cls.__forward__

        assert hasattr(forward_cls, '__init__')
        # if they haven't touched forward_cls.__init__, remove it.
        # (if they set an explicit init it should be in the continue class.)
        if forward_cls.__init__ == forward_cls.__forward_new_init__:
            del forward_cls.__init__
        del forward_cls.__forward_new_init__

        for name, value in continue_cls.__dict__.items():
            if name == "__doc__":
                if not value:
                    continue
            elif name == "__annotations__":
                original = getattr(forward_cls, name, None)
                if original:
                    original.update(value)
                    continue
                # fall through to setattr below
            elif name in dont_overwrite_attributes:
                continue
            if name in existing_attributes:
                continue
            setattr(forward_cls, name, value)

            # fix no-argument super! wow!
            if callable(value) and hasattr(value, "__closure__") and value.__closure__:
                for closure in value.__closure__:
                    if closure.cell_contents == continue_cls:
                        closure.cell_contents = forward_cls

        return forward_cls
    return continue_

__all__ = ["forward", "continue_"]