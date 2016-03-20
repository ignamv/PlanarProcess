from planarprocess import *
from gds_helpers import GdsCut
from itertools import cycle

xmin, xmax = -5, 5
gds = GdsCut('mypmos.gds', [(0,xmin), (0, xmax)], 'gdsmap.map')

['P-Active-Well', 'Active-Cut', 'N-Well', 'Metal-2', 'Metal-1', 'P-Select',
'N-Select', 'Transistor-Poly', 'Via1']

wafer = Wafer(4., 12., xmin, xmax)
nw = gds.layer('N-Well')
wafer.implant(3., nw, outdiffusion=5., label='N-Well')
de = gds.layer('P-Active-Well')
# TODO: channel stop under field oxide
fox = wafer.grow(.5, wafer.blank_mask().difference(de),
        y_offset=-.2, outdiffusion=.1)

gox = wafer.grow(.05, de, outdiffusion=.05, base=wafer.wells, 
        label='Gate oxide')
gp = gds.layer('Transistor-Poly')
poly = wafer.grow(.25, gp, outdiffusion=.25, label='Gate poly')
np = gds.layer('N-Select').intersection(
        gds.layer('P-Active-Well')).difference(gp)
nplus = wafer.implant(.1, np, outdiffusion=.1, target=wafer.wells, source=gox,
        label='N+')
pp = gds.layer('P-Select').intersection(
        gds.layer('P-Active-Well')).difference(gp)
pplus = wafer.implant(.1, pp, outdiffusion=.1, target=wafer.wells, source=gox,
        label='P+')

mld_thickness = .5
mld = wafer.grow(mld_thickness, wafer.blank_mask(), outdiffusion=.1)
ct = gds.layer('Active-Cut')
contact = wafer.grow(-mld_thickness*1.1, ct, consuming=[mld, gox], base=wafer.air,
        outdiffusion=.05, outdiffusion_vertices=3)
m1 = gds.layer('Metal-1')
metal1 = wafer.grow(1., m1, outdiffusion=.1, label='Metal-1')
ild_thickness = 2.
ild1 = wafer.grow(ild_thickness, wafer.blank_mask(), outdiffusion=.1)
wafer.planarize()
v1 = gds.layer('Via1')
via1 = wafer.grow(-ild_thickness*1.1, v1, consuming=[ild1], base=wafer.air,
        outdiffusion=.05, outdiffusion_vertices=3)
m2 = gds.layer('Metal-2')
metal2 = wafer.grow(1., m2, outdiffusion=.1, label='Metal-2')

custom_style = {
    fox: dict(color=(.4,.4,.4)),
    gox: dict(color='r'),
    poly: dict(color='m'),
    mld: dict(color=(.2,.2,.2)),
    ild1: dict(color=(.3,.3,.3)),
    contact: dict(color=(.5,.5,.5)),
    via1: dict(color=(.5,.5,.5)),
    metal1: dict(color=(.7,.7,.7)),
    metal2: dict(color=(.8,.8,.8)),
}
for style in custom_style.values():
    style['fill'] = True
base_hatches = r'\/' # r'/\|-+xoO.*'
hatches = cycle(list(base_hatches) + [h1+h2 for h1 in base_hatches 
        for h2 in base_hatches])
colors = cycle('krgbcmy')
plot_geometryref(wafer.air, hatch='.', fill=False, linewidth=0, color=(.9,.9,.9),
        zorder=-100)
zorder = -99
for solid in wafer.solids:
    style = dict(hatch=next(hatches), fill=False,
            color=next(colors), zorder=zorder)
    zorder += 1
    style.update(custom_style.get(solid, {}))
    plot_geometryref(solid, **style)
pyplot.legend()
pyplot.savefig('out.svg')
pyplot.show()

