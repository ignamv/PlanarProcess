from grow import *

wafer = Wafer(1., 3., -2, 2)
nplus = wafer.implant(.3, [(0,2)], outdiffusion=.1)
nburied = wafer.implant(.3, [(-1,3)], buried=.4, outdiffusion=.1)
m1 = wafer.grow(.2, [(-1.5, 0.5)], outdiffusion=.1)
m2 = wafer.grow(.3, [(-1., 1.)], outdiffusion=.1)
wafer.etch(1., [(-.25, .15)], outdiffusion=.2, outdiffusion_vertices=32)
fox = wafer.grow(.2, [(-.5, 1.5)], outdiffusion=.1, y_offset=-.05)

plot_geometryref(nburied, hatch='\\\\', fill=False, color='c')
plot_geometryref(nplus, hatch='\\', fill=False, color='r')
plot_geometryref(m1, hatch='//', fill=False, color='b')
plot_geometryref(m2, hatch='//', fill=False, color='g')
plot_geometryref(fox, fill=True, color=(.3, .3, .3))
plot_geometryref(wafer.substrate, hatch='/', fill=False, zorder=-998)
plot_geometryref(wafer.air, hatch='.', fill=False, linewidth=0, color=(.9,.9,.9),
        zorder=-999)
pyplot.savefig('out.svg')
pyplot.show()

