import shapely
import shapely.ops
import numpy
import logging
from geometry_helpers import *

logger = logging.getLogger(__name__)

class Wafer(object):
    def __init__(self, substrate_height, maximum_y, minimum_x, maximum_x):
        self.air = GeometryReference(shapely.geometry.box(minimum_x,
            substrate_height, maximum_y, maximum_x))
        self.substrate = GeometryReference(shapely.geometry.box(minimum_x, 0, 
            maximum_x, substrate_height))
        self.solids = [self.substrate]

    def grow(self, height, mask, base=None, consuming=None, outdiffusion=0., 
            etching=False, outdiffusion_vertices=16, y_offset=0.):
        '''Deposit height of material on regions specified by mask.

        base is one or several GeometryReference, over which material is
        deposited. By default, deposit over all solids.
        consuming is one or several GeometryReference, which material can
        grow into. By default, only grow into air.
        outdiffusion is the width of the rounded border, interpolated with 
        outdiffusion_vertices vertices.
        y_offset shifts in the y axis, enabling partially buried growth (for
        example oxidation consuming silicon) and floating structures.
        '''
        if base is None:
            base = self.solids
        if consuming is None:
            consuming = self.air
        base = ensure_list(base)
        consuming = ensure_list(consuming)
        if y_offset != 0 and numpy.sign(y_offset) != numpy.sign(y_offset 
                + height):
            # Partially buried, return union of implant and growth
            base_copy = [b for b in base]
            bottom = self.grow(y_offset, mask, base=consuming,
                    consuming=base, outdiffusion=outdiffusion, etching=etching,
                    outdiffusion_vertices=outdiffusion_vertices)
            top = self.grow(height + y_offset, mask, base=base_copy + [bottom],
                    consuming=consuming, outdiffusion=outdiffusion,
                    etching=etching, 
                    outdiffusion_vertices=outdiffusion_vertices)
            return GeometryReference(top.geometry.union(bottom.geometry))
        base_union = shapely.ops.cascaded_union([b.geometry for b in base])
        consuming_union = shapely.ops.cascaded_union(
                [c.geometry for c in consuming])
        whole_interface = base_union.intersection(consuming_union)
        buried = numpy.sign(height) != numpy.sign(y_offset)
        logger.debug('Growing %f on %s, consuming %s, mask %s, interface %s', 
                height, base_union, consuming_union, mask, whole_interface)
        polygons = []
        for segment in mask:
             interface = ensure_multilinestring(whole_interface.intersection(
                     shapely.geometry.box(segment[0], 0, segment[1],
                         self.air.geometry.bounds[3])))
             for linestring in interface:
                 if not isinstance(linestring, shapely.geometry.LineString):
                     # Don't want Points and other strange bits of the 
                     # intersection
                     continue
                 coords = [(x, y + y_offset) for x,y in linestring.coords]
                 top = [(x, y + height) for x,y in reversed(coords)]
                 polygon = shapely.geometry.Polygon(coords + top)
                 if polygon.area == 0:
                     continue
                 polygons.append(polygon)
                 # Add lateral outgrowth/outdiffusion
                 if outdiffusion != 0.:
                     updown = numpy.sign(height)
                     large_y = 20
                     for x, y in top:
                         if y_offset == 0.:
                             # Outdiffusion is a corner and a pillar to the 
                             # base
                             polygons.append(shapely.geometry.Polygon(
                                 ellipse(x, y - height,
                                     outdiffusion, height,
                                     0, numpy.pi, outdiffusion_vertices)
                                 + [(x - outdiffusion, y - updown * large_y),
                                 (x + outdiffusion, y - updown * large_y)]
                             ))
                         else:
                             # Outdiffusion is a half ellipse
                             polygons.append(shapely.geometry.Polygon(
                                 ellipse(x, y - height / 2,
                                     outdiffusion, height / 2,
                                     0, 2 * numpy.pi, outdiffusion_vertices)))

         # Only consume from specified geometry
        ret = shapely.ops.cascaded_union(polygons).intersection(
                consuming_union)
        for c in consuming:
            c.geometry = c.geometry.difference(ret)
        for b in base:
            b.geometry = b.geometry.difference(ret)
        ret = GeometryReference(ret)
        if not etching:
            self.solids.append(ret)
        return ret

    def etch(self, depth, mask, consuming=None, **kwargs):
        '''Etch depth on regions specified by mask.

        consuming is one or several GeometryReference, which may be etched.
        By default, etch any solid.
        Additional kwargs are explained in grow() documentation.
        '''
        if consuming is None:
            consuming = self.solids
        hole = self.grow(-depth, mask, base=self.air, consuming=consuming,
                etching=True, **kwargs)
        self.air.geometry = self.air.geometry.union(hole.geometry)

    def implant(self, depth, mask, target=None, source=None, buried=0.,
            **kwargs):
        '''Implant to depth where specified by mask.

        target is one or several GeometryReference, which may be implanted.
        By default, implant any solid.
        buried specifies the depth of the top edge of the implant (0 by 
        default).
        Additional kwargs are explained in grow() documentation.
        '''
        if target is None:
            target = self.solids
        if source is None:
            source = self.air
        return self.grow(-depth, mask, base=source, consuming=target,
                y_offset=-buried, **kwargs)
