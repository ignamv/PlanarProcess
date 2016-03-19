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

def circle(center, radius):
    return shapely.geometry.Point(center).buffer(radius)

def pretty():
    sun = circle([0, 0], 1)
    nstars = 6
    for ii in range(nstars):
        angle = 2 * numpy.pi * ii / nstars
        star = circle([numpy.cos(angle), numpy.sin(angle)], .2)
        sun = sun.difference(star)
    plot_geometryref(sun, fill=False, hatch='//')
    pyplot.xlim((-2,2))
    pyplot.ylim((-2,2))
    pyplot.show()

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

def grow(height, segments, base=None, consuming=None, outdiffusion=0., 
        etching=False, outdiffusion_vertices=16):
    global air, solids
    if base is None:
        base = solids
    if consuming is None:
        consuming = air
    base = ensure_list(base)
    consuming = ensure_list(consuming)
    base_union = shapely.ops.cascaded_union([b.geometry for b in base])
    consuming_union = shapely.ops.cascaded_union([c.geometry for c in consuming])
    whole_interface = base_union.intersection(consuming_union)
    logger.debug('Growing %f on %s, consuming %s, segments %s, interface %s', 
            height, base_union, consuming_union, segments, whole_interface)
    polygons = []
    for segment in segments:
         interface = ensure_multilinestring(whole_interface.intersection(
                 shapely.geometry.box(segment[0], 0, segment[1], maxy)))
         for linestring in interface:
             if not isinstance(linestring, shapely.geometry.LineString):
                 continue
             coords = list(linestring.coords)
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
                     polygons.append(shapely.geometry.Polygon(
                         ellipse(x, y - height,
                             outdiffusion, height,
                             0, numpy.pi, outdiffusion_vertices)
                         + [(x - outdiffusion, y - updown * large_y),
                         (x + outdiffusion, y - updown * large_y)]
                     ))
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

def etch(depth, segments, consuming=None, **kwargs):
    if consuming is None:
        consuming = solids
    hole = grow(-depth, segments, base=air, consuming=consuming, etching=True,
            **kwargs)
    air.geometry = air.geometry.union(hole.geometry)

def implant(depth, segments, target=None, source=None, **kwargs):
    if target is None:
        target = solids
    if source is None:
        source = air
    return grow(-depth, segments, base=source, consuming=target, **kwargs)

#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())
substrate = GeometryReference(shapely.geometry.box(-2, 0, 4, 1))
solids.append(substrate)
nplus = implant(.3, [(0,2)], outdiffusion=.1)
m1 = grow(.2, [(-1.5, 0.5)], outdiffusion=.1)
m2 = grow(.3, [(-1., 1.)], outdiffusion=.1)
etch(1., [(-.25, .25)], outdiffusion=.2)
fox = grow(.2, [(-.5, 1.5)], outdiffusion=.1)

plot_geometryref(nplus, hatch='\\', fill=False, color='r')
plot_geometryref(m1, hatch='//', fill=False, color='b')
plot_geometryref(m2, hatch='//', fill=False, color='g')
plot_geometryref(fox, fill=True, color=(.3, .3, .3))
plot_geometryref(substrate, hatch='/', fill=False, zorder=-998)
plot_geometryref(air, hatch='.', fill=False, linewidth=0, color=(.9,.9,.9),
        zorder=-999)
pyplot.savefig('out.svg')
pyplot.show()
