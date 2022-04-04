# tests no-argument super().

from forward import *

@forward()
class Child():
    ...
@continue_(Child)
class _:
    def __init__(self):
        super().__init__()
        self.child = True

o = Child()
assert hasattr(o, "child")

print("no-argument super() is working!")
