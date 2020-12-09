'''
Created on Jun 10, 2020

@author: sjjamsa
'''
import ctypes
import numpy as np

# from header.h or similar
_INFTY=1e37
_COLOURS=256
_MAX_STR=256
_YES = 1
_NO  = 0

_str_encoding='utf-8'

_LIBFILE="libsss2.so"

class sss2():
    """ This class is a wrapper to serpent2.
It's main job is to convert b/w python & numpy types and c types.
"""

    
    def __init__(self,serpent_arguments=None,libfile=None):
        self.SUPPORTED_PYTHONPLOTTER_INTERFACE_VERSION = 12

        
        
        if libfile is None:
            self._soFilename=_LIBFILE
        else:
            self._soFilename=libfile

        print('Loading serpent shared library "'+self._soFilename+'".')
        self._sss2=ctypes.cdll.LoadLibrary(self._soFilename)

        #### init_interactive ####
        self.sss2_main = self._sss2.init_interactive 
        self.sss2_main.restype  =  ctypes.c_int
        # The argtypes of main need to be updated per call because length varies


        #### getGeometryParameters ####
        self.sss2_getGeometryParameters = self._sss2.getGeometryParameters
        self.type_geom_stats = geom_stats
        self.sss2_getGeometryParameters.restype  = ctypes.c_long
        self.sss2_getGeometryParameters.argtypes = [ctypes.POINTER(self.type_geom_stats)]


        #### getNumberOfMaterials ####
        self.sss2_getNumberOfMaterials = self._sss2.getNumberOfMaterials
        self.sss2_getNumberOfMaterials.restype = ctypes.c_long
        self.sss2_getNumberOfMaterials.argtypes = [ctypes.POINTER(ctypes.c_long)]

        #### getMaterials ####
        self.sss2_getMaterials = self._sss2.getMaterials
        self.sss2_getMaterials.restype = ctypes.c_long
        # The argtypes need to be updated per call because length varies

        #### getPositionInfo ####
        self.sss2_getPositionInfo = self._sss2.getPositionInfo
        self.sss2_getPositionInfo.restype = ctypes.c_long
        # The argtypes need to be updated per call because length varies
        
        #### free ####
        self.sss2_free = self._sss2.free_interactive
        self.sss2_free.restype = ctypes.c_int
        self.sss2_free.argtypes = []

        #### getVersion ####
        self.sss2_getVersion = self._sss2.getVersion
        self.sss2_getVersion.restype = ctypes.c_long
        self.sss2_getVersion.argtypes = [ctypes.POINTER(ctypes.c_char*_MAX_STR) , ctypes.POINTER(ctypes.c_long)]



        ### plotImage ###
        self.sss2_plotImage = self._sss2.PlotImage
        self.sss2_plotImage.restype = ctypes.c_long
        # The argtypes need to be updated per call because length varies
        
        ### PutPlotColors
        self.sss2_putPlotColors = self._sss2.PutPlotColors
        self.sss2_putPlotColors.argtypes=[ctypes.c_long,  #im
                                          ctypes.POINTER(ctypes.c_long * _COLOURS), # *R 
                                          ctypes.POINTER(ctypes.c_long * _COLOURS), # *G
                                          ctypes.POINTER(ctypes.c_long * _COLOURS), # *B
                                          ]
        

        if not serpent_arguments is None:
            _ = self.start_run(serpent_arguments)
            

    def getGenuineImage(self,
                        xp:int, yp:int,
                        xmin:float, xmax:float, ymin:float, ymax:float,
                        position:float, plot_plane:int,
                        boundaries : int=2, particle_type : int=2, 
                        scale : int=0, E : float = 1.0 , fmin : float = 1.0, fmax : float=10.0, 
                        quickplot : int= 0 ):
        '''
         Use the engine of the Serpent command line plotter to generate images.

         Required parameters:
         xp           : int    plot size in pixels
         yp           : int    plot size in pixels
         xmin         : float  first  plot axis minimum value (see plot_plane)
         xmax         : float  first  plot axis maximum value (see plot_plane)
         ymin         : float  second plot axis minimum value (see plot_plane)
         ymax         : float  second plot axis maximum value (see plot_plane)
         position     : float  The off-plane coordinate (e.g. z-coordinate for xy-plot)
         plot_plane   : int    1 = yz, 2 = xz, 3 = xy

         Optional parameters (default values:
         boundaries   : int=2           plot boundaries? [0 = none, 1 = cell, 2 = material, 3 = both]
         particle_type: int=0           neutron=2, gamma = 1 (defined in header.h)
         scale        : int=0           0=no importance plot, 1,3=lin-scale, 2=log-scale
         E            : float=1.0       Energy for importance plots (MeV)
         fmin         : float=1.0       min value for importance plots
         fmax         : float=10.0      max value for importance plots
         quickplot    : int=0           0=quickplot-off, 1=quickplot-on
        '''
        
        npixels = xp * yp
        
        self.sss2_plotImage.argtypes = [ctypes.POINTER(ctypes.c_long*npixels), # The image
                                        ctypes.c_long,ctypes.c_long,           # image size
                                        ctypes.c_double, ctypes.c_double,      # xmin, xmax
                                        ctypes.c_double, ctypes.c_double,      # ymin, ymax
                                        ctypes.c_double, ctypes.c_double,      # zmin, zmax
                                        ctypes.c_double,                       # position of the plane
                                        ctypes.c_long,                         # plot boundaries
                                        ctypes.c_long,                         # particle type (neutron=2, gamma = 1 (header.h))
                                        ctypes.c_long,                         # plot plane (1 = yz, 2 = xz, 3 = xy).
                                        ctypes.c_long,                         # scale (log/lin...)
                                        ctypes.c_double,                       # energy (importance)
                                        ctypes.c_double, ctypes.c_double,      # min max values (importance)
                                        ctypes.c_long,                         # quickplot mode                                       
                                        ]
#long *mtx1, long xp, long yp, double xmin,
#               double xmax, double ymin, double ymax, double zmin,
#               double zmax, double pos, long bou, long par, long ax,
#               long scale, double E, double fmin, double fmax, long qp
               
        
        if plot_plane == 1:
            minx = -_INFTY;   maxx =  _INFTY
            miny = xmin;   maxy = xmax
            minz = ymin;   maxz = ymax
        elif plot_plane == 2:
            minx = xmin;   maxx = xmax
            miny = -_INFTY;   maxy =  _INFTY
            minz = ymin;   maxz = ymax
        elif plot_plane == 3:
            minx = xmin;   maxx = xmax
            miny = ymin;   maxy = ymax
            minz = -_INFTY;   maxz =  _INFTY
        else:
            raise ValueError("plot_plane should be 1 = yz, 2 = xz or 3 = xy, but got {}.".format(plot_plane))
        
        image_c = (ctypes.c_long*npixels)()
        for i in range(npixels):
            image_c[i]=-2
        status = self.sss2_plotImage(ctypes.pointer(image_c), xp, yp,
                                     minx, maxx, miny, maxy, minz, maxz,
                                     position,
                                     boundaries,
                                     particle_type,
                                     plot_plane,
                                     scale,E,fmin,fmax,
                                     quickplot)
        if status!= 0:
            print('plotImage return status was {}, continuing.'.format(status))        

        
        image = -1*np.ones(shape=(xp*yp,),dtype=int)
        image[:] = image_c
        
        #return image_c
        
        image = np.flipud( np.reshape(image,(xp,yp)).T )

        #Shall we use importance plotting colorscale?
        if scale > 0:
            im = _YES
        else:
            im = _NO
        R = (ctypes.c_long * _COLOURS )()
        G = (ctypes.c_long * _COLOURS )()
        B = (ctypes.c_long * _COLOURS )()
        self.sss2_putPlotColors(im,ctypes.pointer(R),ctypes.pointer(G),ctypes.pointer(B))
        
        colormap = np.zeros(shape=(_COLOURS,3),dtype=int)
        for i in range(len(R)):
            colormap[i,0] = R[i]
            colormap[i,1] = G[i]
            colormap[i,2] = B[i]

        return image,colormap


    def getGeometryParameters(self):
        """
        Reads the geometry limits from Serpent.
"""

        gs = geom_stats()
        gs_p = self.type_geom_stats.from_address(ctypes.addressof(gs))
        status = self.sss2_getGeometryParameters(gs_p)

        if status != 0:
            print('getGeometryParameters return status was {}, continuing.'.format(status))

        return gs


            
    def start_run(self,serpent_arguments):
        """ Start serpent with the parameters given in serpent_arguments.
        serpent_arguments : List of strings
        """
        
        # Start by checking the version
        
        #serpent_version= (ctypes.c_char * _MAX_STR)()
        serpent_version = ctypes.create_string_buffer(_MAX_STR)
        pythonplotter_version = ctypes.c_long()
        
        self.sss2_getVersion(ctypes.byref(serpent_version),ctypes.byref(pythonplotter_version))
                
        print('Serpent version {}'.format(serpent_version.value.decode(_str_encoding)))
        print('Python plotter interface version {}'.format(pythonplotter_version.value))
        
        self.check_pythonplotter_version(pythonplotter_version.value)
        
        
        if not type(serpent_arguments) is list:
            raise ValueError('The serpent_arguments is not a List, it is {}'.format(str(type(serpent_arguments))))

        nargs = len(serpent_arguments)+2

        args = (ctypes.c_char_p * nargs)()
        args[0]= bytes("pysss2", _str_encoding)
        for i,p in enumerate(serpent_arguments):
            if not type(p) is str :
                raise ValueError("Serpent Argument {} is not a string.".format(i))
            args[i+1]=bytes(p, _str_encoding)

        self.sss2_main.argtypes = [ctypes.c_int,ctypes.c_char_p*nargs ] # This needs to be update per call

        
        status = self.sss2_main(len(serpent_arguments)+1, args)

        if status != 0:
            print('sss2 main() returned {}. Continuing still.'.format(status))


        return status

    def check_pythonplotter_version(self,pythonplotter_version):

        
        if pythonplotter_version != self.SUPPORTED_PYTHONPLOTTER_INTERFACE_VERSION:

            raise RuntimeError("Wrong version of python plotter ({}), version {} needed.".format(
                pythonplotter_version, self.SUPPORTED_PYTHONPLOTTER_INTERFACE_VERSION))


    def get_materials(self):
        
        nMaterials = ctypes.c_long()
        status = self.sss2_getNumberOfMaterials(ctypes.byref(nMaterials))
        if status != 0:
            print('getNumberOfMaterials return status was {}, continuing with {} materials.'.format(status,nMaterials))        
        
        n = nMaterials.value
        

        materials = ( material* n )()
        self.sss2_getMaterials.argtypes = [ material*n, ]
        status = self.sss2_getMaterials(materials)
        if status!= 0:
            print('getMaterials return status was {}, continuing.'.format(status))        

        return materials

#    def plot_geometry(self,M=None):
#        if M is None:
#            M = self.get_geometryPlot()
#        print('Plotting')
#        plt.imshow(M)
#        plt.colorbar()
#        plt.show()

    def get_positionInfo(self,xarr,yarr,zarr):

        n=len(xarr)
        if len(yarr) != n or len(zarr) != n:
            raise ValueError('xarr,yarr,zarr must be same size')

        pinfos = ( pinfo* n )()
        self.sss2_getPositionInfo.argtypes = [ ctypes.c_long, pinfo*n, ]
        
        for i in range(n):
            pinfos[i].x=xarr[i]
            pinfos[i].y=yarr[i]
            pinfos[i].z=zarr[i]
            pinfos[i].time=0.0
        
        status = self.sss2_getPositionInfo(n,pinfos)
        if status!= 0:
            print('getPositionInfo return status was {}, continuing.'.format(status))        

        return pinfos

    

class geom_stats(ctypes.Structure):
    ''' See pythonplotter.h for the C definition
    '''
    
    _fields_ = [('xmin',ctypes.c_double),
                ('xmax',ctypes.c_double),
                ('ymin',ctypes.c_double),
                ('ymax',ctypes.c_double),
                ('zmin',ctypes.c_double),
                ('zmax',ctypes.c_double)  ]

class material(ctypes.Structure):
    ''' See pythonplotter.h for the C definition

   '''
    _fields_ =[('density',           ctypes.c_double   ),       #  g/cm3 
               ('color',             ctypes.c_long * 3 ),       #  R,G,B 
               ('numberOfNuclides',  ctypes.c_long     ),       #  For a future implementation of a routine that reads the nuclide list.
               ('name',              ctypes.c_char * _MAX_STR)] #  Null terminated 


class pinfo(ctypes.Structure):
    ''' This struct reflects the C definition

    '''
    _fields_ =[('x',             ctypes.c_double         ),       #  cm 
               ('y',             ctypes.c_double         ),       #  cm 
               ('z',             ctypes.c_double         ),       #  cm 
               ('time',          ctypes.c_double         ),       #  IGNORED 
               ('universe',      ctypes.c_long           ),       #  
               ('universe_name', ctypes.c_char * _MAX_STR),       #  Null terminated   
               ('cell',          ctypes.c_long           ),       #  
               ('cell_name',     ctypes.c_char * _MAX_STR),       #   
               ('material',      ctypes.c_long           ),       #  
               ('material_name', ctypes.c_char * _MAX_STR), 
               ('material_color_RGB',ctypes.c_long * 3   ),      #   
               ]                                                   
    def __str__(self):
        out = ""
        out += "(x,y,z)=({},{},{})\n".format(self.x,self.y,self.z)
        out += "univ {:3d}:{}\n".format(self.universe,self.universe_name.decode(_str_encoding))
        out += "cell {:3d}:{}\n".format(self.cell,    self.cell_name.decode(_str_encoding))
        out += "mat  {:3d}:{}\n".format(self.material,    self.material_name.decode(_str_encoding))
        out += "mat_color {:3d},{:3d},{:3d}\n".format(
            self.material_color_RGB[0],     self.material_color_RGB[1],     self.material_color_RGB[2] )

        return out
        