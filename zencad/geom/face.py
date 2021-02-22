import math

import OCC.Core.BRepPrimAPI
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_EDGE
from OCC.Core.gp import gp_Circ, gp, gp_Pnt
from OCC.Core.GC import GC_MakeCircle
import OCC.Core.Addons


from zencad.lazifier import *
from zencad.shape import Shape, nocached_shape_generator, shape_generator
from zencad.util import as_indexed
import zencad.util
from zencad.util import deg, point3
from zencad.geom.sew import _sew
import zencad.geom.wire as wire
import zencad.geom.wire as wire_module
import zencad.geom.curve as curve
from zencad.geom.trans import rotateZ


def _fill(shp):
    assert(shp.Shape().ShapeType() in (TopAbs_WIRE, TopAbs_EDGE))
    return Shape(BRepBuilderAPI_MakeFace(shp.Wire_orEdgeToWire()).Face())


@lazy.lazy(cls=nocached_shape_generator)
def fill(shp):
    return _fill(shp)


@lazy.lazy(cls=nocached_shape_generator)
def polygon(pnts, wire=False):
    wr = wire_module.polysegment(pnts, closed=True)
    return wr if wire else fill(wr)


@lazy.lazy(cls=nocached_shape_generator)
def rectangle_wire(a, b, center):
    if center:
        x = a / 2
        y = b / 2
        return wire.polysegment([(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)], True)
    else:
        return wire.polysegment([(0, 0, 0), (a, 0, 0), (a, b, 0), (0, b, 0)], True)


@lazy.lazy(cls=nocached_shape_generator)
def rectangle(a, b=None, center=False, wire=False):
    if b is None:
        b = a

    wr = rectangle_wire(a, b, center)
    if wire:
        return wr
    else:
        return fill(wr)


def square(*args, **kwargs):
    return rectangle(*args, **kwargs)


def _circle_edge(r, angle=None):
    if angle is None:
        #EL = gp_Circ(gp.XOY(), r)
        #anCircle = GC_MakeCircle(EL).Value();
        # return Shape(BRepBuilderAPI_MakeEdge( anCircle ).Edge())
        return wire._make_edge(curve._circle(r))

    else:
        angle = zencad.util.angle_pair(angle)
        #EL = gp_Circ(gp.XOY(), r)
        #anCircle = GC_MakeCircle(EL).Value();
        # return Shape(BRepBuilderAPI_MakeEdge( anCircle, angle[0], angle[1] ).Edge())
        return wire._make_edge(curve._circle(r), angle)


def _circle(r, angle=None, wire=False):
    if wire is True:
        return _circle_edge(r, angle)

    else:
        if angle is None:
            return _fill(_circle_edge(r))

        else:
            angle = zencad.util.angle_pair(angle)
            a1, a2 = angle[0], angle[1]

            aEdge = _circle_edge(r, angle).Edge()
            aEdge1 = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(
                r * math.cos(a1), r * math.sin(a1), 0)).Edge()
            aEdge2 = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(
                r * math.cos(a2), r * math.sin(a2), 0)).Edge()
            aCircle = BRepBuilderAPI_MakeWire(aEdge, aEdge1, aEdge2).Wire()
            return Shape(BRepBuilderAPI_MakeFace(aCircle).Face())


@lazy.lazy(cls=nocached_shape_generator)
def circle(r, angle=None, wire=False):
    return _circle(r, angle, wire)


def _ngon(r, n, wire=False):
    pnts = [0] * n

    for i in range(n):
        angle = 2 * math.pi / n * i
        pnts[i] = point3(r * math.cos(angle), r * math.sin(angle), 0)

    if wire:
        return wire_module.polysegment(pnts, closed=True)
    return polygon(pnts)


@lazy.lazy(cls=nocached_shape_generator)
def ngon(r, n, wire=False):
    return _ngon(r, n, wire)


def register_font(fontpath):
    OCC.Core.Addons.register_font(fontpath)


@lazy.lazy(cls=nocached_shape_generator)
def textshape(text, fontname, size, composite_curve=False):
    aspect = OCC.Core.Addons.Font_FA_Regular
    textshp = OCC.Core.Addons.text_to_brep(text, fontname,
                                           aspect, size, composite_curve)

    return Shape(textshp)


def _ellipse(r1, r2, angle=None, wire=True):
    if r2 > r1:
        inversed_sizes = True
        r1, r2 = r2, r1
    else:
        inversed_sizes = False

    crv = curve._ellipse(r1, r2)

    if angle:
        angle = zencad.util.angle_pair(angle)
        edg = wire_module._make_edge(crv, angle)

        if not wire:
            ret = edg
        else:
            ucrv = crv
            p1 = ucrv._d0(angle[0])
            p2 = ucrv._d0(angle[1])

            wr = _sew([edg,
                       wire_module._segment(p1, (0, 0)),
                       wire_module._segment(p2, (0, 0))])
            ret = _fill(wr)

    else:
        edg = wire_module._make_edge(crv)
        ret = edg if wire else fill(edg)

    if inversed_sizes:
        return rotateZ(deg(90))(ret)
    else:
        return ret


@lazy.lazy(cls=nocached_shape_generator)
def ellipse(r1, r2, angle=None, wire=True):
    return _ellipse(r1, r2, angle, wire)