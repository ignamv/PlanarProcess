from planarprocess import *
from gds_helpers import GdsCut
from itertools import cycle

xmin, xmax = -5, 5
gds = GdsCut('mypmos.gds', [(0,xmin), (0, xmax)], 'gdsmap.map')

['P-Active-Well', 'Active-Cut', 'N-Well', 'Metal-2', 'Metal-1', 'P-Select',
'N-Select', 'Transistor-Poly', 'Via1']

custom_style = {}
wafer = Wafer(10., 12., xmin, xmax)
nw = gds.layer('N-Well')
wafer.implant(5., nw, outdiffusion=5.)
de = gds.layer('P-Active-Well')
# TODO: channel stop under field oxide
fox = wafer.grow(.5, wafer.blank_mask().difference(de),
        y_offset=-.1, outdiffusion=.1)

gox = wafer.grow(.05, de, outdiffusion=.05, base=wafer.wells)
gp = gds.layer('Transistor-Poly')
wafer.grow(.25, gp, outdiffusion=.25)
np = gds.layer('N-Select').intersection(
        gds.layer('P-Active-Well')).difference(gp)
nplus = wafer.implant(.1, np, outdiffusion=.1, target=wafer.wells, source=gox)
pp = gds.layer('P-Select').intersection(
        gds.layer('P-Active-Well')).difference(gp)
pplus = wafer.implant(.1, pp, outdiffusion=.1, target=wafer.wells, source=gox)

ild_thickness = .5
ild = wafer.grow(ild_thickness, wafer.blank_mask(), outdiffusion=.1)
ct = gds.layer('Active-Cut')
#wafer.etch(ild_thickness*1.1, ct, consuming=[ild, gox])
contact = wafer.grow(-ild_thickness*1.1, ct, consuming=[ild, gox], base=wafer.air,
        outdiffusion=.05, outdiffusion_vertices=3)

custom_style[fox] = dict(fill=True, color=(.4,.4,.4), hatch=None)
custom_style[gox] = dict(fill=True, color='r', hatch=None)
custom_style[ild] = dict(fill=True, color=(.2,.2,.2), hatch=None)
custom_style[contact] = dict(fill=True, color=(.5,.5,.5), hatch=None)
base_hatches = r'/\|-+xoO.*'
hatches = iter(list(base_hatches) + [h1+h2 for h1 in base_hatches 
        for h2 in base_hatches])
colors = cycle('krgbcmy')
plot_geometryref(wafer.air, hatch='.', fill=False, linewidth=0, color=(.9,.9,.9),
        zorder=-1)
zorder = 0
for solid in wafer.solids:
    style = dict(hatch=next(hatches), fill=False,
            color=next(colors), zorder=zorder)
    zorder += 1
    style.update(custom_style.get(solid, {}))
    plot_geometryref(solid, **style)
pyplot.savefig('out.svg')
pyplot.show()

