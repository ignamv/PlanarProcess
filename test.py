from planarprocess import *
from gds_helpers import *
from itertools import cycle

xmin, xmax = -5, 5
layers = gds_cross_section('mypmos.gds', [(0,xmin), (0, xmax)], 'gdsmap.map')

['P-Active-Well', 'Active-Cut', 'N-Well', 'Metal-2', 'Metal-1', 'P-Select',
'N-Select', 'Transistor-Poly', 'Via1']

wafer = Wafer(1., 5., 0, xmax - xmin)

# N-Well
nw = layers['N-Well']
wafer.implant(.7, nw, outdiffusion=5., label='N-Well')

# Field and gate oxides
de = layers['P-Active-Well']
# TODO: channel stop under field oxide
fox = wafer.grow(.5, wafer.blank_mask().difference(de),
        y_offset=-.2, outdiffusion=.1)
gox = wafer.grow(.05, de, outdiffusion=.05, base=wafer.wells, 
        label='Gate oxide')

# Gate poly and N+/P+ implants
gp = layers['Transistor-Poly']
poly = wafer.grow(.25, gp, outdiffusion=.25, label='Gate poly')
np = layers['N-Select'].intersection(
        layers['P-Active-Well']).difference(gp)
nplus = wafer.implant(.1, np, outdiffusion=.1, target=wafer.wells, source=gox,
        label='N+')
pp = layers['P-Select'].intersection(
        layers['P-Active-Well']).difference(gp)
pplus = wafer.implant(.1, pp, outdiffusion=.1, target=wafer.wells, source=gox,
        label='P+')

# Multi-level dielectric and contacts
mld_thickness = .5
mld = wafer.grow(mld_thickness, wafer.blank_mask(), outdiffusion=.1)
ct = layers['Active-Cut']
contact = wafer.grow(-mld_thickness*1.1, ct, consuming=[mld, gox], base=wafer.air,
        outdiffusion=.05, outdiffusion_vertices=3)

# Metals and vias
m1 = layers['Metal-1']
metal1 = wafer.grow(.6, m1, outdiffusion=.1, label='Metal-1')
ild_thickness = 1.2
ild1 = wafer.grow(ild_thickness, wafer.blank_mask(), outdiffusion=.1)
wafer.planarize()
v1 = layers['Via1']
via1 = wafer.grow(-ild_thickness*1.1, v1, consuming=[ild1], base=wafer.air,
        outdiffusion=.05, outdiffusion_vertices=3)
m2 = layers['Metal-2']
metal2 = wafer.grow(1., m2, outdiffusion=.1, label='Metal-2')

# Presentation
custom_style = {s: {} for s in wafer.solids}
for solid, color in {
        fox: '.4', gox: 'r', poly: 'g', mld: 'k',
        ild1: '.3', contact: '.5', via1: '.5',
        metal1: '.7', metal2: '.8'}.items():
    custom_style[solid].update(dict(facecolor=color, edgecolor='k'))

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
pyplot.legend()
pyplot.savefig('mypmos-x.png')
pyplot.show()

