
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())
substrate = GeometryReference(shapely.geometry.box(-2, 0, 4, 1))
solids.append(substrate)
nplus = implant(.3, [(0,2)], outdiffusion=.1)
nburied = implant(.3, [(-1,3)], buried=.4, outdiffusion=.1)
m1 = grow(.2, [(-1.5, 0.5)], outdiffusion=.1)
m2 = grow(.3, [(-1., 1.)], outdiffusion=.1)
etch(1., [(-.25, .15)], outdiffusion=.2, outdiffusion_vertices=32)
fox = grow(.2, [(-.5, 1.5)], outdiffusion=.1, y_offset=-.05)
#fox_mask = [(-.5, 1.5)]
#fox = implant(.05, fox_mask, outdiffusion=.1)
#fox.geometry = fox.geometry.union(
        #grow(.1, fox_mask, outdiffusion=.1).geometry)

plot_geometryref(nburied, hatch='\\\\', fill=False, color='c')
plot_geometryref(nplus, hatch='\\', fill=False, color='r')
plot_geometryref(m1, hatch='//', fill=False, color='b')
plot_geometryref(m2, hatch='//', fill=False, color='g')
plot_geometryref(fox, fill=True, color=(.3, .3, .3))
#plot_geometryref(fox1, fill=True, color=(.3, .3, .3))
#plot_geometryref(fox2, fill=True, color=(.3, .3, .3))
plot_geometryref(substrate, hatch='/', fill=False, zorder=-998)
plot_geometryref(air, hatch='.', fill=False, linewidth=0, color=(.9,.9,.9),
        zorder=-999)
pyplot.savefig('out.svg')
pyplot.show()

