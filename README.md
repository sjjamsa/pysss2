# pysss2
Python tools to interact with Serpent2 Monte Carlo code

The key resource at the moment is the GUI to inspect Serpent2 geometries interactively.
How to use it:

1) Compile Serpent2 in a dedicated folder with interactive plotter settings on. At the time of writing (between Serpent versions 2.1.31 and 2.1.32) you need to have in Makefile:
   CFLAGS  += -DINTERACTIVE_PLOTTER -fPIC
   libsss2.so : $(OBJS)
           $(CC) -shared $(OBJS) $(LDFLAGS) -o $@

2) In your serpent input file you need to have at least one "plot" card

3) When running pysss2, 
   a) you need to either add the folder of libsss2.so in LD_LIBRARY_PATH or specify the absolute path to the file as the first two parameters: "pysss2 --libsss2so /absolute/path/to/libsss2.so ...". Rest of the parameters are passed to serpent2.
   b) you *must* give the parameter -interactiveplotter to serpent2: "pysss2 --libsss2so /absolute/path/to/libsss2.so -interactiveplotter ..."
A full example:  "pysss2 --libsss2so /absolute/path/to/libsss2.so -interactiveplotter model -omp 4"