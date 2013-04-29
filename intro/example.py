"""
This file demonstrates the usage for the final working form of the Python C
Extension, using an object-oriented approach to provide the same functionality
as the original C form.
"""
import sys
sys.path.append("build/lib.linux-i686-2.6")
import mything


if __name__ == "__main__":
    thinger = mything.MyThing()
    thing1 = thinger.get_thing_one()
    thing2 = thinger.get_thing_two()
    print "\nThing One: %i\nThing Two: %i\n" % (thing1, thing2)
