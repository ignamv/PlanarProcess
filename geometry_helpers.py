import shapely
import matplotlib
from matplotlib import pyplot
import numpy

def ensure_multipolygon(polygons):
    '''Use in functions which return either Polygon or MultiPolygon'''
    if isinstance(polygons, shapely.geometry.Polygon):
        return shapely.geometry.MultiPolygon([polygons])
    else:
        return polygons

def ensure_multilinestring(lines):
    '''Use in functions which return either LineString or MultiLineString'''
    if isinstance(lines, shapely.geometry.LineString):
        return shapely.geometry.MultiLineString([lines])
    else:
        return lines

def ensure_list(item_or_list):
    '''If not a list, pack inside a list.'''
    if isinstance(item_or_list, list):
        return item_or_list
    else:
        return [item_or_list]

def plot_geometryref(geometryref, axes=None, **kwargs):
    '''Plot geometry referenced by geometryref'''
    if axes is None:
        axes = pyplot.gca()
    polygons = ensure_multipolygon(geometryref.geometry)
    if geometryref.label is not None and 'label' not in kwargs:
        kwargs['label'] = geometryref.label
    for polygon in polygons:
        xy = numpy.column_stack( polygon.exterior.xy)
        axes.add_patch(matplotlib.patches.Polygon(xy, **kwargs))
        axes.update_datalim(zip(polygon.bounds[::2], polygon.bounds[1::2]))
        # Only first polygon needs a legend entry
        kwargs.pop('label', None)
    axes.autoscale()

def multilinestring_to_segments(multilinestring):
    return [[point[1] for point in segment.coords] 
            for segment in ensure_multilinestring(multilinestring)]

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


