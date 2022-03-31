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

def forward():
    def forward(cls):
        cls.__forward__ = True
        name = cls.__name__
        message = f"{name} is a forward-declared class"
        def __init__(self, *a, **kw):
            raise TypeError(message)
        cls.__forward_original_init__ = getattr(cls, '__init__', None)
        cls.__forward_new_init__ = __init__
        cls.__init__ = __init__
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

        assert hasattr(forward_cls, '__forward_original_init__')
        assert hasattr(forward_cls, '__forward_new_init__')
        assert hasattr(forward_cls, '__init__')
        if forward_cls.__init__ == forward_cls.__forward_new_init__:
            if forward_cls.__forward_original_init__ == None:
                # print(f"{forward_cls.__name__}: deleting init")
                del forward_cls.__init__
            else:
                # print(f"{forward_cls.__name__}: restoring original init {forward_cls.__forward_original_init__}")
                forward_cls.__init__ = forward_cls.__forward_original_init__
            # del forward_cls.__init__
        del forward_cls.__forward_original_init__
        del forward_cls.__forward_new_init__

        for name, value in continue_cls.__dict__.items():
            if name == "__doc__":
                if not value:
                    continue
            if name == "__annotations__":
                original = getattr(forward_cls, name, None)
                if original:
                    original.update(value)
                    continue
                # fall through to setattr below
            if name in dont_overwrite_attributes:
                continue
            if name in existing_attributes:
                continue
            setattr(forward_cls, name, value)

        return forward_cls
    return continue_

__all__ = ["forward", "continue_"]