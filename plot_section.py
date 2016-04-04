from matplotlib import pyplot
from itertools import cycle
from geometry_helpers import plot_geometryref

def present(wafer):
    custom_style = {s: {} for s in wafer.solids}
    for solid in wafer.solids:
        if solid not in wafer.wells:
            custom_style[solid].update(dict(hatch=None, fill=True))

    base_hatches = r'\/' # r'/\|-+xoO.*'
    hatches = cycle(list(base_hatches) + [h1+h2 for h1 in base_hatches 
            for h2 in base_hatches])
    colors = cycle('krgbcmy')
    plot_geometryref(wafer.air, hatch='.', fill=False, linewidth=0, color=(.9,.9,.9),
            zorder=-100)
    zorder = -99
    for solid in wafer.solids:
        style = dict(hatch=next(hatches), fill=False,
                edgecolor=next(colors), zorder=zorder)
        zorder += 1
        style.update(custom_style.get(solid, {}))
        plot_geometryref(solid, **style)
