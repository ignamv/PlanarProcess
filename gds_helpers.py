import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Ignore dxfgrabber warning
    import gdsCAD
from shapely import geometry
import re
from geometry_helpers import *

def gds_cross_section(gds_file, cut_segment, layer_map=None):
    '''Return a {layer: [cross section intervals]} mapping for a GDS file

    gds_file: input GDS filename
    cut_segment: list of vertices of segment defining the cross section
    layer_map: optional filename for GDS map file. If present, the returned
    dictionary's keys will be layer names instead of numbers.'''
    cut_segment = geometry.LineString(cut_segment)
    cell = list(gdsCAD.core.GdsImport(gds_file).values())[0]
    layers = {layer: polygons_to_cross_section(polygons, cut_segment)
            for layer, polygons in list(cell_to_MultiPolygon(cell).items())}
    if layer_map is None:
        self.layers = layers
    else:
        layer_map = load_gds_map(layer_map)
        layers = {layer_map[layer]: geometry 
                for layer, geometry in list(layers.items())}
    return layers

def load_gds_map(filename):
    '''Return number->name mapping from gds map file'''
    layers = {}
    input_file = open(filename)
    gds_map_regex = re.compile(r'(?P<name>[a-zA-Z0-9\-]+)\s+'
                '(?P<purpose>[a-zA-Z0-9]+)\s+(?P<number>\d+)\s+(?P<datatype>\d+)\s*$')
    for line in input_file:
        match = gds_map_regex.match(line)
        if not match:
            continue
        fields = match.groupdict()
        layers[int(fields['number'])] = fields['name']
    return layers

def cell_to_MultiPolygon(cell):
    '''Create dict with a geometry.MultiPolygon for each layer in GDS cell'''
    layers = {layer: [] for layer in cell.get_layers()}
    for boundary in cell.objects:
        layers[boundary.layer].append(boundary_to_polygon(boundary))
    return layers

def boundary_to_polygon(boundary):
    '''Convert gdsCAD.core.Boundary to geometry.Polygon'''
    if not isinstance(boundary, gdsCAD.core.Boundary):
        raise TypeError('Expected boundary, got {}'.format(repr(boundary)))
    # No need to repeat first point
    if all(boundary.points[0] == boundary.points[-1]):
        points = boundary.points[:-1]
    else:
        points = boundary.points
    return geometry.Polygon(points)
