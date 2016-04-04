from planarprocess import *
from gds_helpers import *
from itertools import cycle
from plot_section import present
from matplotlib import pyplot

xmin, xmax = -8, 8
layers = gds_cross_section('nwell.gds', [(0,xmin), (0, xmax)], 'gdsmap.map')

wafer = Wafer(1., 5., 0, xmax - xmin)

# N-Well
nw = layers['N-Well']
print nw
wafer.implant(.7, nw, outdiffusion=0., label='N-Well')
present(wafer)
pyplot.legend()
pyplot.show()
