# Demonstrates using slots with forward.

from forward import *

@forward()
class Zotz:
    __slots__ = ('a', 'b')

@continue_(Zotz)
class _:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def print(self):
        print(f"a = {self.a} and b = {self.b}, and zot's all!")

z = Zotz(33, 44)
z.print()
print("Does z have a dict?", "yes." if hasattr(z, '__dict__') else "no.")
