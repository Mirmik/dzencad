#!/usr/bin/env python3
#coding: utf-8

from zencad import *
test_mode()

m = sphere(10) - halfspace().rotateX(deg(30))

display(m)

show()