# pysss2 #
Python tools to interact with Serpent 2 Monte Carlo code 

*Pysss2 C-side code is expected to be released with Serpent 2.1.32*. Until then, the Serpent 2 development version is needed.


The key resource provided by this package is the **GUI to inspect Serpent 2 geometries interactively**. The program allows interactive plotting of various cross sections: xy, xz or yz slices. The plot limits and the number of pixels can be chosen and the resulting figures can be saved. Also the material, cell and universe of a point can be checked.


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
* The blue button:
  * *eval pos* Evaluates the material, cell and universe in the point clicked with mouse. The results are shown in the status bar and printed in the terminal.
* The red buttons:
  * *Reload* Restarts the plotter, forcing Serpent to regenerate the geometry (e.g. after the input has been changed).
  * *Quit* Exits the program.


When the python program launches, it launches serpent as a library using ctypes. 
The python side of the code only accepts a single optional  first parameter:  "--libsss2so /path/to/libsss2.so". All the rest are passed on to serpent un-parsed. In other words, the other parameters are serpent's parameters, not for the python.

## How to install and run the GUI: ##

1. **Install pysss2 with pip**, as explained in the [pypi page](https://pypi.org/project/pysss2/) of the project.
   1. The code uses python 3. It is known to work at least with version 3.6.7. You can check the current with e.g. 
   "python3 -c "import sys; print(sys.version)".
   2. There was [a bug in matplotlib](https://github.com/matplotlib/matplotlib/issues/14781), so 'matplotlib>=3.1.1' is needed. You can check the current version with e.g. "python3 -c "import matplotlib; print(matplotlib.__version__)"

2.  **Compile the "lib" target (possibly in a dedicated folder) with the -fpic setting enabled in Makefile.** (That is, uncomment the line _"CFLAGS += -fpic"_. Then run _"make clean"_  and then _"make lib"_. The result should be a shared library called libssss2.so. This file includes all the routines of serpent, but they can be called from other programs.

3. In your serpent input file you need to **define colors for all materials** (e.g. "rgb 10 20 30").

4. When running pysss2, the python code must know where to find the libssss2.so shared library. Thus, you need to either add the folder of libsss2.so in LD_LIBRARY_PATH environment or specify the absolute path to the file as the first two parameters: "pysss2 --libsss2so /absolute/path/to/libsss2.so ...". Rest of the parameters are passed to serpent.
Here is a full example:  **"pysss2 --libsss2so /absolute/path/to/libsss2.so -interactiveplotter model -omp 4"**.
