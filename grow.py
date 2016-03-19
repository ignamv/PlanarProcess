import matplotlib
from matplotlib import pyplot
import shapely.geometry
import shapely.ops
import shapely.ops 
import numpy
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

maxy = 4
air = GeometryReference(shapely.geometry.box(-2, 1, 4, maxy))
solids = []

def grow(base, height, segments, consuming=None, etching=False):
    global air
    if consuming is None:
        consuming = [air]
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
             coords = list(linestring.coords)
             polygon = shapely.geometry.Polygon(
                 coords + [(x, y + height) for x,y in reversed(coords)])
             if polygon.area == 0:
                 continue
             # Only consume from specified geometry
             polygon = polygon.intersection(consuming_union)
             polygons.append(polygon)
    ret = shapely.ops.cascaded_union(polygons)
    for c in consuming:
        c.geometry = c.geometry.difference(ret)
    for b in base:
        b.geometry = b.geometry.difference(ret)
    ret = GeometryReference(ret)
    if not etching:
        global solids
        solids.append(ret)
    return ret

def etch(consuming, depth, segments):
    hole = grow(air, -depth, segments, consuming, True)
    air.geometry = air.geometry.union(hole.geometry)

logger.addHandler(logging.StreamHandler())
substrate = GeometryReference(shapely.geometry.box(-2, 0, 4, 1))
solids.append(substrate)
nplus = grow(air, -.1, [(0,2)], consuming=substrate)
m1 = grow([substrate,nplus], .2, [(-1.5, 0.5)])
m2 = grow([substrate, nplus, m1], .3, [(-1., 1.)])
etch(solids, 1., [(-.25, .25)])

plot_geometryref(nplus, hatch='\\', fill=False, color='r')
plot_geometryref(m1, hatch='//', fill=False, color='b')
plot_geometryref(m2, hatch='//', fill=False, color='g')
plot_geometryref(substrate, hatch='/', fill=False, zorder=-998)
plot_geometryref(air, hatch='.', fill=False, linewidth=0, color=(.9,.9,.9),
        zorder=-999)
pyplot.savefig('out.svg')
pyplot.show()
