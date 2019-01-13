#!/usr/bin/env python3
#coding: utf-8

from zencad import *
import zencad.surface as surface
import zencad.curve2 as curve2

height = 70
width = 50
thickness = 30

pnt1 = point(-width/2.,0,0);
pnt2 = point(-width/2.,-thickness/4.,0);
pnt3 = point(0,-thickness/2.,0);
pnt4 = point(width/2,-thickness/4.,0);
pnt5 = point(width/2.,0,0);

edge1 = segment(pnt1, pnt2)
edge2 = circle_arc(pnt2, pnt3, pnt4)
edge3 = segment(pnt4, pnt5)

wire = sew([edge1, edge2, edge3])
profile = sew([wire, wire.mirrorX()])

body = profile.fill().extrude(height).fillet(thickness/12)

neck_radius = thickness/4.;
neck_height = height/10;

neck = cylinder(r=neck_radius, h=neck_height).up(height)

body = body + neck
body = thicksolid(body, point(0,0,height+height/10), -thickness / 50)

cylsurf1 = surface.cylinder(neck_radius * 0.99)
cylsurf2 = surface.cylinder(neck_radius * 1.05)

major = 2 * math.pi;
minor = neck_height / 10;

ellipse1 = curve2.ellipse(major, minor)
ellipse2 = curve2.ellipse(major, minor)

arc1 = curve2.trimmed_curve2(ellipse1, 0, math.pi)

display(body)
show()