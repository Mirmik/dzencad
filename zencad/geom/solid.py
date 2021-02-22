from zencad.shape import Shape, nocached_shape_generator
from zencad.util import as_indexed, angle_pair
import OCC.Core.BRepPrimAPI
from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Vec, gp_Dir, gp_Pln
from OCC.Core.BRepLib import BRepLib_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace

from zencad.lazifier import *


@lazy.lazy(cls=nocached_shape_generator)
def box(size, y=None, z=None, center=None):
    if isinstance(size, (float, int)):
        x = size
        if y is None and z is None:
            size = (x, x, x)
        else:
            if z is None:
                size = (x, y, 0)
            else:
                size = (x, y, z)

    x, y, z = size[0], size[1], size[2]

    if center:
        ax2 = gp_Ax2(gp_Pnt(-x / 2, -y / 2, -z / 2), gp_Dir(0, 0, 1))
        return Shape(OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeBox(ax2, *size).Shape())
    else:
        return Shape(OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeBox(*size).Shape())


@lazy.lazy(cls=nocached_shape_generator)
def sphere(r, yaw=None, pitch=None):
    if yaw is None and pitch is None:
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeSphere(r).Shape()
    elif yaw is None and pitch is not None:
        pitch = angle_pair(pitch)
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeSphere(
            r, pitch[0], pitch[1]).Shape()
    elif yaw is not None and pitch is None:
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeSphere(r, yaw).Shape()
    else:
        pitch = angle_pair(pitch)
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeSphere(
            r, pitch[0], pitch[1], yaw).Shape()

    return Shape(raw)


@lazy.lazy(cls=nocached_shape_generator)
def cylinder(r, h, yaw=None, center=False):
    if center:
        ax2 = gp_Ax2(gp_Pnt(0, 0, -h/2), gp_Dir(0, 0, 1))
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeCylinder(ax2, r, h).Shape()
        return Shape(raw)
    else:
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeCylinder(r, h).Shape()
        return Shape(raw)


@lazy.lazy(cls=nocached_shape_generator)
def cone(r1, r2, h, yaw=None, center=False):
    if center:
        ax2 = gp_Ax2(gp_Pnt(0, 0, -h / 2), gp_Dir(0, 0, 1))
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeCone(ax2, r1, r2, h).Shape()
        return Shape(raw)
    else:
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeCone(r1, r2, h).Shape()
        return Shape(raw)


@lazy.lazy(cls=nocached_shape_generator)
def torus(r1, r2, yaw=None, pitch=None):
    if yaw is None and pitch is None:
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeTorus(r1, r2).Shape()
    elif yaw is None and pitch is not None:
        pitch = angle_pair(pitch)
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeTorus(
            r1, r2, pitch[0], pitch[1]).Shape()
    elif yaw is not None and pitch is None:
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeTorus(r1, r2, yaw).Shape()
    else:
        pitch = angle_pair(pitch)
        raw = OCC.Core.BRepPrimAPI.BRepPrimAPI_MakeTorus(
            r1, r2, pitch[0], pitch[1], yaw).Shape()

    return Shape(raw)


@lazy.lazy(cls=nocached_shape_generator)
def halfspace():
    F = BRepLib_MakeFace(gp_Pln()).Face()
    MHS = BRepPrimAPI_MakeHalfSpace(F, gp_Pnt(0, 0, -1))
    return Shape(MHS.Solid())