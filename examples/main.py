#!/usr/bin/env python3

# Demo of "forward" prototype by Larry Hastings, March 2022.
# This software is placed in the public domain or under the CC0-1.0-Universal license, whichever is more permissive.
import x

try:
    i = x.ImportantFunctionality("first try")
    import sys
    sys.exit("This shouldn't work!  We shouldn't get here!")
except TypeError:
    # this is expected
    pass


import x_impl

i = x.ImportantFunctionality("second try")
i.print()

j = x.HandmadeAnnotations("handmade")
j.print()
