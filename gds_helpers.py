import gdsCAD
import shapely
import shapely.affinity
import re
from geometry_helpers import ensure_multilinestring

class GdsCut(object):
    def __init__(self, gds_file, cut_segment, layer_map=None):
        cell = gdsCAD.core.GdsImport(gds_file).values()[0]
        layers = GdsCut.cell_to_MultiPolygon(cell)
        if layer_map is None:
            self.layers = layers
        else:
            layer_map = GdsCut.load_gds_map(layer_map)
            self.layers = {layer_map[layer]: geometry 
                    for layer, geometry in layers.items()}
        self.cut_segment = shapely.geometry.LineString(cut_segment)

    def layer(self, name):
        return GdsCut.cut_project(self.layers[name], self.cut_segment)

    @staticmethod
    def load_gds_map(filename):
        '''Return number->name mapping from gds map file'''
        layers = {}
        input_file = open(filename)
        gds_map_regex = re.compile('(?P<name>[a-zA-Z0-9\-]+)\t+'
                '(?P<purpose>[a-zA-Z0-9]+)\t(?P<number>\d+)\t(?P<datatype>\d+)$')
        for line in input_file:
            match = gds_map_regex.match(line)
            if not match:
                continue
            fields = match.groupdict()
            layers[int(fields['number'])] = fields['name']
        return layers

    @staticmethod
    def boundary_to_polygon(boundary):
        '''Convert gdsCAD.core.Boundary to shapely.geometry.Polygon'''
        if not isinstance(boundary, gdsCAD.core.Boundary):
            raise TypeError('Expected boundary, got {}'.format(repr(boundary)))
        # No need to repeat first point
        if all(boundary.points[0] == boundary.points[-1]):
            points = boundary.points[:-1]
        else:
            points = boundary.points
        return shapely.geometry.Polygon(points)

    @staticmethod
    def cell_to_MultiPolygon(cell):
        '''Create dict with a shapely.geometry.MultiPolygon for each layer'''
        layers = {layer: shapely.geometry.MultiPolygon([]) for layer in cell.get_layers()}
        for boundary in cell.objects:
            layers[boundary.layer] = layers[boundary.layer].union(
                    GdsCut.boundary_to_polygon(boundary))
        return layers

    @staticmethod
    def cut_project(geometry, cut_segment):
        '''Return y-axis intervals where geometry intersects cut_segment'''
        intersection = geometry.intersection(cut_segment)
        # Project to the y axis
        # TODO: project to cut segment
        return shapely.affinity.scale(intersection, 0,1,0, (0,0,0))
