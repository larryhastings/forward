# Demo of "forward" prototype by Larry Hastings, March 2022.
# This software is placed in the public domain or under the CC0-1.0-Universal license, whichever is more permissive.
from forward import *
import x


@continue_(x.NecessaryBaseClass)
class _____:
    pass


@continue_(x.ImportantFunctionality)
class _____:

    def __init__(self, s):
        self.s = s

    def print(self):
        print("ImportantFunctionality:", self.s)


@continue_(x.HandmadeAnnotations)
class _:
    a:int = 0

    def __init__(self, s):
        self.s = s

    def print(self):
        print("HandmadeAnnotations:", self.s, self.a, self.b, self.__annotations__)
