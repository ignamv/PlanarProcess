Integrated circuit cross-sections from GDS files
==

This set of classes allows you to take an IC layout like this:

![IC Layout](https://github.com/ignamv/PlanarProcess/raw/master/mypmos.png "IC Layout")

along with a description of the fabrication process, and produce a
cross-section like this:

![IC Cross section](https://github.com/ignamv/PlanarProcess/raw/master/mypmos-x.png "IC Cross Section")

The fastest way to get started is to look at test.py and modify it to suit
your needs. There are three distinct parts to it:

* Load a GDS file and its layer map

* Execute process steps (deposition, diffusion, etc) using data from the GDS
  layers

* Present the resulting cross-section choosing color, hatching patterns, etc.

Inspiration came from the 
[XSection plugin for KLayout](https://sourceforge.net/p/xsectionklayout/wiki/DocIntro/).
