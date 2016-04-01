from matplotlib import pyplot as plt
import shapely.geometry
from geometry_helpers import *

gap = 0.00
original_coords = [  (0,0), (3,0), (3, 1.5-gap), 
            (2,1.5-gap), (2,1), (1,1), (1,2), (2.2,2), (2.2,1.5+gap),
            (2.8,1.5+gap), (2.8,3), (0,3)]
original_segments = map(shapely.geometry.LineString, zip(original_coords[:-1],
    original_coords[1:]))
# Split segments at every intersection
all_coords = []
for ii, segmentA in enumerate(original_segments):
    all_coords.append(original_coords[ii])
    for jj, coordB in reversed(list(enumerate(original_coords))):
        if segmentA.contains(shapely.geometry.Point(coordB)) and \
                coordB not in segmentA.coords:
            # Split this segment
            all_coords.append(coordB)
            segmentA = shapely.geometry.LineString([coordB,
                segmentA.coords[1]])
all_coords.append(segmentA.coords[1])
print all_coords

# Separate interior from exterior
processed = []
# Lists of coords left to process
pending = [(0, len(all_coords))]
while pending:
    first, last = pending.pop()
    current = []
    ii = first
    while ii < last:
        coordA = all_coords[ii]
        current.append(coordA)
        for jj in range(last-1, ii, -1):
            if coordA == all_coords[jj]:
                pending.append((ii+1, jj-1))
                ii = jj
                break
        ii += 1
    processed.append(current)

print processed
#plot_geometryref(GeometryReference(holey))
from itertools import cycle
colors = cycle('rgbcmyk')
for p in processed:
    plt.plot(*zip(*p), linestyle='solid', marker='x', color=next(colors))
#plt.plot(*zip(*exterior), linestyle='solid', marker='o', color='b')
plt.show()
