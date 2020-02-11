# pysss2 #
Python tools to interact with Serpent2 Monte Carlo code

*Pysss2 C-side code is expected to be released with Serpent 2.1.32*. Until then, the Serpent 2 development version is needed.


The key resource at the moment is the **GUI to inspect Serpent 2 geometries interactively**. The program allows interactive plotting of various cross sections: xy, xz or yz slices. The plot limits and the number of pixels can be chosen and the resulting figures can be saved.


## Usage (buttons on the right) ##
* Gray buttons change the view limits on the bar on top
  * *Geom. Limits* resets the default limts 
  * *View to limits* moves the current  zoomed in/out limits to the top bar
* Green buttons updates the plots in addition to changing the values
  * *View to limits & Upd* is just updating version of the gray button
  * *V2L & P1:1 & Upd* does the same as above, but also tries to set the number of pixels to match the number of pixels on the displaying screen
  * *V2L & P1:10 & Upd* does the same as above, but only has one calculated pixel for each 10x10 screen pixels
* Yellow buttons change the slice (XY, XZ or YZ) to view:
  * *to ?? & Upd* After clicking a yellow button, click on the plot to choose the location for the new slice
* The red buttons:
  * *Reload* Restarts the plotter, forcing Serpent to regenerate the geometry (e.g. after the input has been changed).
  * *Quit* Exits the program.


When the python program launches, it launches serpent as a library using ctypes. 
The python side of the code only accepts a single optional  first parameter:  "--libsss2so /path/to/libsss2.so". All the rest are passed on to serpent un-parsed. In other words, the other parameters are serpent's parameters, not for the python.

## How to install the GUI: ##

1. Compile Serpent2 in a dedicated folder with interactive plotter settings on. At the time of writing (between Serpent versions 2.1.31 and 2.1.32) you need to have in the Serpent Makefile:

```Makefile
CFLAGS  += -DINTERACTIVE_PLOTTER -fPIC
libsss2.so : $(OBJS)
	$(CC) -shared $(OBJS) $(LDFLAGS) -o $@
```

2. In your serpent input file you need to 
  1. have at least one "plot" card
  2. define colors for all materials (e.g. "rgb 10 20 30")

3. When running pysss2, 
   1. you need to either add the folder of libsss2.so in LD_LIBRARY_PATH or specify the absolute path to the file as the first two parameters: "pysss2 --libsss2so /absolute/path/to/libsss2.so ...". Rest of the parameters are passed to serpent2.
   2. you *must* give the parameter -interactiveplotter to serpent2: "pysss2 --libsss2so /absolute/path/to/libsss2.so -interactiveplotter ..."

A full example:  "pysss2 --libsss2so /absolute/path/to/libsss2.so -interactiveplotter model -omp 4"
