# Demonstrates stacked decorators.

from forward import *

@forward()
class X:
    ...

print(f"       forward class {X.__name__!r}, id: {hex(id(X))}")

def dekorator(cls):
    print(f"dekorator sees class {X.__name__!r}, id: {hex(id(X))}")

@dekorator
@continue_(X)
class _:
    a = 3
