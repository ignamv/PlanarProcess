from shapely import geometry
import matplotlib
from matplotlib import pyplot
import numpy

def ensure_multipolygon(polygons):
    '''Use in functions which return either Polygon or MultiPolygon'''
    if isinstance(polygons, geometry.Polygon):
        return geometry.MultiPolygon([polygons])
    else:
        return polygons

def ensure_multilinestring(lines):
    '''Use in functions which return either LineString or MultiLineString'''
    if isinstance(lines, geometry.LineString):
        return geometry.MultiLineString([lines])
    else:
        return lines

def ensure_list(item_or_list):
    '''If not a list, pack inside a list.'''
    if isinstance(item_or_list, list):
        return item_or_list
    else:
        return [item_or_list]

def plot_geometry(geometry, axes=None, **kwargs):
    if axes is None:
        axes = pyplot.gca()
    polygons = ensure_multipolygon(geometry)
    for polygon in polygons.geoms:
        xy = numpy.column_stack( polygon.exterior.xy)
        axes.add_patch(matplotlib.patches.Polygon(xy, **kwargs))
        axes.update_datalim(list(zip(polygon.bounds[::2], polygon.bounds[1::2])))
        # Only first polygon needs a legend entry
        kwargs.pop('label', None)
    axes.autoscale()

def polygon_edges(polygon):
    coords = polygon.boundary.coords
    return (geometry.LineString([pointA, pointB]) 
            for pointA, pointB in zip(coords[:-1], coords[1:]))

def plot_geometryref(geometryref, axes=None, **kwargs):
    '''Plot geometry referenced by geometryref'''
    if geometryref.label is not None and 'label' not in kwargs:
        kwargs['label'] = geometryref.label
    plot_geometry(geometryref.geometry, axes, **kwargs)

def multilinestring_to_segments(multilinestring):
    return [[point[0] for point in segment.coords] 
            for segment in ensure_multilinestring(multilinestring).geoms]

class GeometryReference(object):
    '''Pointer to shapely geometry'''
    def __init__(self, geometry, label=None):
        self.geometry = geometry
        self.label = label

def ellipse(x, y, width, height, theta0, theta1, nvertices):
    '''List of vertices for ellipse section with semi-axes weight,height'''
    return [(x + width * numpy.cos(theta),
             y + height * numpy.sin(theta))
             for theta in numpy.linspace(theta0, theta1, nvertices)]

def polygons_to_cross_section(polygons, cut_segment):
    cuts = [0., cut_segment.length]
    for polygon in polygons:
        for side in polygon_edges(polygon):
            intersection = cut_segment.project(
                    cut_segment.intersection(side))
            if intersection > cuts[0] and intersection < cuts[-1] \
                    and intersection not in cuts:
                index = next((ii for ii, element in enumerate(cuts) 
                        if element > intersection))
                cuts.insert(index, intersection)
    present = [False] * (len(cuts) - 1)
    for polygon in polygons:
        for ii, already_present in enumerate(present):
            if not already_present:
                present[ii] |= polygon.contains(cut_segment.interpolate(
                    .5 * (cuts[ii] + cuts[ii + 1])))
    return geometry.MultiLineString([
        [(cuts1, 0), (cuts2, 0)] for cuts1, cuts2, present in zip(
        cuts[:-1], cuts[1:], present) if present])

def parse_path(svg_path_d):
    def parse_coords(part):
        return tuple(float(c) for c in part.split(','))
    parts = iter(svg_path_d.split())
    coords = []
    for part in parts:
        if part == 'm':
            coords.append(parse_coords(next(parts)))
        elif part == 'z':
            continue # ???
        else:
            coords.append(tuple(previous + delta for previous, delta in zip(
                coords[-1], parse_coords(part))))
    return coords

#holey = geometry.Polygon(parse_path("m 200,612.3622 200,0 0,-160 -60,0 0,120\
    #-100,0 0,-60 100,0 0,-60 -140,0 z"))
#triangle = geometry.Polygon(parse_path('m 280,392.3622 -40,20 95,15 z'))
#segment = geometry.LineString(parse_path('m 255,382.3622 165,330'))
#print polygons_to_cross_section([holey, triangle], segment)
