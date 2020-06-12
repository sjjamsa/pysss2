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

_str_encoding='utf-8'

_LIBFILE="libsss2.so"

class sss2():
    """ This class is a wrapper to serpent2.
It's main job is to convert b/w python & numpy types and c types.
"""
    
    def __init__(self,serpent_arguments=None,libfile=None):
        if libfile is None:
            self._soFilename=_LIBFILE
        else:
            self._soFilename=libfile

        print('Loading serpent shared library "'+self._soFilename+'".')
        self._sss2=ctypes.cdll.LoadLibrary(self._soFilename)

        self.sss2_main = self._sss2.main 
        self.sss2_main.restype  =  ctypes.c_int
        # The argtypes of main need to be updated per call because length varies

        self.sss2_getGeometryPlotMatrix = self._sss2.getGeometryPlotMatrix
        self.sss2_getGeometryPlotMatrix.restype  =  ctypes.c_long
        # The argtypes need to be updated per call because length varies


        self.sss2_getGeometryParameters = self._sss2.getGeometryParameters
        self.type_geom_stats = geom_stats
        self.sss2_getGeometryParameters.restype  = ctypes.c_long
        self.sss2_getGeometryParameters.argtypes = [ctypes.POINTER(self.type_geom_stats)]

        #print('Testing the struct thing')
        #gs = self.getGeometryParameters()
        #print('geom_stats',gs)
        #print('xmin=',gs.xmin,' xmax=',gs.xmax)
        #print('ymin=',gs.ymin,' xmax=',gs.ymax)
        #print('zmin=',gs.zmin,' xmax=',gs.zmax)
        #print('')


        self.sss2_getNumberOfMaterials = self._sss2.getNumberOfMaterials
        self.sss2_getNumberOfMaterials.restype = ctypes.c_long
        self.sss2_getNumberOfMaterials.argtypes = [ctypes.POINTER(ctypes.c_long)]

        self.sss2_getMaterials = self._sss2.getMaterials
        self.sss2_getMaterials.restype = ctypes.c_long
        # The argtypes need to be updated per call because length varies

        #print('Testing the materials thing')
        #materials = self.get_materials()
        #print( 'len(materials)=',len(materials) )
        #print( 'materials=',materials)
        #for m in materials:
        #    print('"'+m.name.decode(_str_encoding)+'"')
        #    print('density',m.density)
        #    print('color',m.color[:])

        self.sss2_getPositionInfo = self._sss2.getPositionInfo
        self.sss2_getPositionInfo.restype = ctypes.c_long
        # The argtypes need to be updated per call because length varies
        



        if not serpent_arguments is None:
            status = self.start_run(serpent_arguments)

        

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


    def get_geometryPlot_raw(self,
                         plane, xpix, ypix, pos,
                         xmin=-_INFTY, xmax=_INFTY, 
                         ymin=-_INFTY, ymax=_INFTY,
                         zmin=-_INFTY, zmax=_INFTY):
        """
        Get a single plot from Serpent.
        """



        nPix =  xpix * ypix
        nCol =  3 * _COLOURS

        self.sss2_getGeometryPlotMatrix.argtypes = [ctypes.c_long, # (plane), 
                                                    ctypes.c_long, # (xpix),
                                                    ctypes.c_long, # (ypix), 
                                                    ctypes.c_double, # (pos),
                                                    ctypes.c_double, # (xmin), 
                                                    ctypes.c_double, # (xmax),
                                                    ctypes.c_double, # (ymin), 
                                                    ctypes.c_double, # (ymax),
                                                    ctypes.c_double, # (zmin), 
                                                    ctypes.c_double, # (zmax),
                                                    ctypes.c_long * nPix, # (matrix),
                                                    ctypes.c_long * nCol  # (rgb)
                                                    ]

        # The datatypes are 1D-arrays of longs.
        matrix = (ctypes.c_long * nPix)()
        rgb    = (ctypes.c_long * nCol)()
        status = self.sss2_getGeometryPlotMatrix(ctypes.c_long(plane), 
                                                  ctypes.c_long(xpix),
                                                  ctypes.c_long(ypix), 
                                                  ctypes.c_double(pos),
                                                  ctypes.c_double(xmin), 
                                                  ctypes.c_double(xmax),
                                                  ctypes.c_double(ymin), 
                                                  ctypes.c_double(ymax),
                                                  ctypes.c_double(zmin), 
                                                  ctypes.c_double(zmax),
                                                  matrix, rgb)
        if status != 0:
            print('sss2 getGeometryPlotMatrix() returned {}. Continuing still.'.format(status))



        M   = np.reshape(np.frombuffer(matrix,dtype=int),(xpix,ypix) ) 
        colorPalette = np.reshape(np.frombuffer(rgb,dtype=int),(_COLOURS,3) )

        # We need to take the transpose.
        M = M.T
    

        # Fix a historical thing...
        if plane == 3:
            M = np.flipud(M)

        # Matplotlib expects to have colors in the 0...1 scale
        cp = colorPalette / 255.0

        return M,cp


    def get_geometryPlot(self,
                         plane, xpix, ypix, pos,
                         min1=_INFTY, max1=_INFTY, 
                         min2=_INFTY, max2=_INFTY):
        if plane == 'xy' or plane == 3:
            xmin = min1
            xmax = max1
            ymin = min2
            ymax = max2
            zmin = -_INFTY
            zmax =  _INFTY
            nplane = 3

        elif plane == 'xz' or plane == 2:
            xmin = min1
            xmax = max1
            ymin = -_INFTY
            ymax =  _INFTY
            zmin = min2
            zmax = max2
            nplane = 2

        elif plane == 'yz' or plane == 1:
            xmin = -_INFTY
            xmax =  _INFTY
            ymin = min1
            ymax = max1
            zmin = min2
            zmax = max2
            nplane = 1

        else:
            raise RuntimeError('Unexpected type of plot "'+str(plane)+'"!') 
        
        return self.get_geometryPlot_raw(
            plane=nplane, xpix=xpix, ypix=ypix, pos=pos,
            xmin=xmin, xmax=xmax, 
            ymin=ymin, ymax=ymax,
            zmin=zmin, zmax=zmax)


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
        