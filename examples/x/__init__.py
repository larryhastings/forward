# Demo of "forward" prototype by Larry Hastings, March 2022.
# This software is placed in the public domain or under the CC0-1.0-Universal license, whichever is more permissive.
from forward import *

@forward()
class ImportantFunctionality:
    ...

@forward()
class HandmadeAnnotations:
    ...

HandmadeAnnotations.b = 0
HandmadeAnnotations.__annotations__ = {'b': int}

