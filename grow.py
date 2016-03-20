import matplotlib
from matplotlib import pyplot
import shapely.geometry
import shapely.ops
import shapely.ops 
import numpy
import logging

logger = logging.getLogger(__name__)

def ensure_multipolygon(polygons):
    if isinstance(polygons, shapely.geometry.Polygon):
        return shapely.geometry.MultiPolygon([polygons])
    else:
        return polygons

def ensure_multilinestring(lines):
    if isinstance(lines, shapely.geometry.LineString):
        return shapely.geometry.MultiLineString([lines])
    else:
        return lines

def ensure_list(item_or_list):
    if isinstance(item_or_list, list):
        return item_or_list
    else:
        return [item_or_list]

def plot_geometryref(geometryref, axes=None, **kwargs):
    if axes is None:
        axes = pyplot.gca()
    polygons = ensure_multipolygon(geometryref.geometry)
    for polygon in polygons:
        xy = numpy.column_stack( polygon.exterior.xy)
        axes.add_patch(matplotlib.patches.Polygon(xy, **kwargs))
        axes.update_datalim(zip(polygon.bounds[::2], polygon.bounds[1::2]))
    axes.autoscale()

class GeometryReference(object):
    def __init__(self, geometry):
        self.geometry = geometry

def ellipse(x, y, width, height, theta0, theta1, nvertices):
    return [(x + width * numpy.cos(theta),
             y + height * numpy.sin(theta))
             for theta in numpy.linspace(theta0, theta1, nvertices)]

maxy = 4
air = GeometryReference(shapely.geometry.box(-2, 1, 4, maxy))
solids = []

def grow(height, mask, base=None, consuming=None, outdiffusion=0., 
        etching=False, outdiffusion_vertices=16, y_offset=0.):
    global air, solids
    if base is None:
        base = solids
    if consuming is None:
        consuming = air
    base = ensure_list(base)
    consuming = ensure_list(consuming)
    if y_offset != 0 and numpy.sign(y_offset) != numpy.sign(y_offset + height):
        # Partially buried, return union of implant and growth
        base_copy = [b for b in base]
        bottom = grow(y_offset, mask, base=consuming,
                consuming=base, outdiffusion=outdiffusion, etching=etching,
                outdiffusion_vertices=outdiffusion_vertices)
        top = grow(height + y_offset, mask, base=base_copy + [bottom],
                consuming=consuming, outdiffusion=outdiffusion,
                etching=etching, outdiffusion_vertices=outdiffusion_vertices)
        return GeometryReference(top.geometry.union(bottom.geometry))
    base_union = shapely.ops.cascaded_union([b.geometry for b in base])
    consuming_union = shapely.ops.cascaded_union([c.geometry for c in consuming])
    whole_interface = base_union.intersection(consuming_union)
    buried = numpy.sign(height) != numpy.sign(y_offset)
    logger.debug('Growing %f on %s, consuming %s, mask %s, interface %s', 
            height, base_union, consuming_union, mask, whole_interface)
    polygons = []
    for segment in mask:
         interface = ensure_multilinestring(whole_interface.intersection(
                 shapely.geometry.box(segment[0], 0, segment[1], maxy)))
         for linestring in interface:
             if not isinstance(linestring, shapely.geometry.LineString):
                 # Don't want Points and other strange bits of the intersection
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
                         polygons.append(shapely.geometry.Polygon(
                             ellipse(x, y - height,
                                 outdiffusion, height,
                                 0, numpy.pi, outdiffusion_vertices)
                             + [(x - outdiffusion, y - updown * large_y),
                             (x + outdiffusion, y - updown * large_y)]
                         ))
                     else:
                         polygons.append(shapely.geometry.Polygon(
                             ellipse(x, y - height / 2,
                                 outdiffusion, height / 2,
                                 0, 2 * numpy.pi, outdiffusion_vertices)))

     # Only consume from specified geometry
    ret = shapely.ops.cascaded_union(polygons).intersection(consuming_union)
    for c in consuming:
        c.geometry = c.geometry.difference(ret)
    for b in base:
        b.geometry = b.geometry.difference(ret)
    ret = GeometryReference(ret)
    if not etching:
        solids.append(ret)
    return ret

def etch(depth, mask, consuming=None, **kwargs):
    if consuming is None:
        consuming = solids
    hole = grow(-depth, mask, base=air, consuming=consuming, etching=True,
            **kwargs)
    air.geometry = air.geometry.union(hole.geometry)

def implant(depth, mask, target=None, source=None, buried=0., **kwargs):
    if target is None:
        target = solids
    if source is None:
        source = air
    return grow(-depth, mask, base=source, consuming=target,
            y_offset=-buried, **kwargs)

#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())
substrate = GeometryReference(shapely.geometry.box(-2, 0, 4, 1))
solids.append(substrate)
nplus = implant(.3, [(0,2)], outdiffusion=.1)
nburied = implant(.3, [(-1,3)], buried=.4, outdiffusion=.1)
m1 = grow(.2, [(-1.5, 0.5)], outdiffusion=.1)
m2 = grow(.3, [(-1., 1.)], outdiffusion=.1)
etch(1., [(-.25, .15)], outdiffusion=.2, outdiffusion_vertices=32)
fox = grow(.2, [(-.5, 1.5)], outdiffusion=.1, y_offset=-.05)
#fox_mask = [(-.5, 1.5)]
#fox = implant(.05, fox_mask, outdiffusion=.1)
#fox.geometry = fox.geometry.union(
        #grow(.1, fox_mask, outdiffusion=.1).geometry)

plot_geometryref(nburied, hatch='\\\\', fill=False, color='c')
plot_geometryref(nplus, hatch='\\', fill=False, color='r')
plot_geometryref(m1, hatch='//', fill=False, color='b')
plot_geometryref(m2, hatch='//', fill=False, color='g')
plot_geometryref(fox, fill=True, color=(.3, .3, .3))
#plot_geometryref(fox1, fill=True, color=(.3, .3, .3))
#plot_geometryref(fox2, fill=True, color=(.3, .3, .3))
plot_geometryref(substrate, hatch='/', fill=False, zorder=-998)
plot_geometryref(air, hatch='.', fill=False, linewidth=0, color=(.9,.9,.9),
        zorder=-999)
pyplot.savefig('out.svg')
pyplot.show()
