#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Test cases for mything bindings module.'''
import unittest
import mything


class MyThingTestCase(unittest.TestCase):

    def setUp(self):
        self.mything = mything.MyThing()

    def test_get_thing1(self):
        self.assertEqual(self.mything.get_thine_one(), 1)

    def test_get_thing2(self):
        self.assertEqual(self.mything.get_thine_two(), 2)


if __name__ == '__main__':
    unittest.main()

