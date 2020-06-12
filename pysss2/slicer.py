'''
Created on Jun 11, 2020

@author: sjjamsa
'''

import pysss2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.colorbar

from pysss2.libsss2 import _str_encoding
from matplotlib import cm

class cartesian_plotter(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def get_materials(self):
        
        matnum    = np.empty(shape=(self.nx,self.ny  ),dtype=int)
        matind    = np.empty(shape=(self.nx,self.ny,2),dtype=int)
        for ix in range(self.nx):
            for iy in range(self.ny):
                matind[   ix,iy,:]   = [ix,iy]
                matnum[   ix,iy  ]   = self.pinfo_array[ix,iy].material

        matnum  = np.reshape(matnum,newshape=(self.nx*self.ny    ))
        matind  = np.reshape(matind,newshape=(self.nx*self.ny, 2 ))

        uniquenums,inds = np.unique(matnum,return_index=True)

        n=len(uniquenums)
        colors = np.empty(shape=(n,3),dtype=int)
        names=[]
        for i in range(n):
            ix = matind[inds[i],0]
            iy = matind[inds[i],1]
            colors[i,:] = self.pinfo_array[ix,iy].material_color_RGB
            names.append(self.pinfo_array[ix,iy].material_name.decode(_str_encoding))
            
        return names,colors
    
    def mk_colormap(self):
        names,colors = self.get_materials()
        
        n=len(names)
        
        cm = matplotlib.colors.ListedColormap(colors=colors/255.0,name='serpentCB',N=n)
        
        return cm,names

    def mk_colorbar(self,fig):
        
        cm,names=self.mk_colormap()
            
        n=len(names)
        bounds = np.arange(1,n+1,1,dtype=int)
        
        
        
        norm = matplotlib.colors.Normalize(vmin=0.5,vmax=n+0.5)
        sm = plt.cm.ScalarMappable(cmap=cm, norm=norm)
        sm.set_array([])
        cb=fig.colorbar(sm, ticks=bounds)
        
        #cb.set_ticks(bounds) 
        cb.set_ticklabels(names)      
        #cb = matplotlib.colorbar.ColorbarBase(cmap=cm,ticks=bounds)
        #cb = plt.colorbar(cmap=cm,ticks=bounds)
        
        return cb
        
    def from_cartesian(self,n1,n2,cut_type,min1,max1,min2,max2,d3):
        '''
        Generate the point arrays on "xy", "xz", or "yz" -planes (cut_type)
        '''
        
        if   cut_type=='xy':
            origin = (min1,min2,d3)
            p1     = (max1,min2,d3)
            p2     = (min1,max2,d3)
        elif cut_type=='xz':
            origin = (min1,d3,min2)
            p1     = (max1,d3,min2)
            p2     = (min1,d3,max2)
        elif cut_type=='yz':
            origin = (d3,min1,min2)
            p1     = (d3,max1,min2)
            p2     = (d3,min1,max2)
        else:
            raise ValueError('Unknown cut_type "{}"'.format(cut_type))

        self.from_3points(origin, p1, p2, n1, n2)

        if   cut_type=='xy':
            self.x_label='x (cm)'
            self.y_label='y (cm)'
        elif cut_type=='xz':
            self.x_label='x (cm)'
            self.y_label='z (cm)'
        elif cut_type=='yz':
            self.x_label='y (cm)'
            self.y_label='z (cm)'

        self.xmin = min1
        self.xmax = max1
        self.ymin = min2
        self.ymax = max2

        

    def from_3points(self,origin,p1,p2,n1,n2):
        '''
        @param origin:  tuple or vector length 3, (x,y,z) [cm]
                        location of the bottom left corner of the slice
        @param p1:  tuple or vector length 3, (x,y,z) [cm]
                        location of the bottom right corner of the slice
        @param p2:  tuple or vector length 3, (x,y,z) [cm]
                        location of the top left corner of the slice
        @param n1:  int
                    number of points in abscissa direction
        @param n2:  int
                    number of points in ordinate direction
        '''


        # Generate vectors 
        x1_vec = np.linspace(0.0,p1[0]-origin[0],n1)
        x2_vec = np.linspace(0.0,p2[0]-origin[0],n2)
        
        y1_vec = np.linspace(0.0,p1[1]-origin[1],n1)
        y2_vec = np.linspace(0.0,p2[1]-origin[1],n2)

        z1_vec = np.linspace(0.0,p1[2]-origin[2],n1)
        z2_vec = np.linspace(0.0,p2[2]-origin[2],n2)

        ix = 'ij'
        xarr1,xarr2 = np.meshgrid(x1_vec,x2_vec,indexing=ix)
        yarr1,yarr2 = np.meshgrid(y1_vec,y2_vec,indexing=ix)
        zarr1,zarr2 = np.meshgrid(z1_vec,z2_vec,indexing=ix)
        self.xarr = xarr1 + xarr2 + origin[0]
        self.yarr = yarr1 + yarr2 + origin[1]
        self.zarr = zarr1 + zarr2 + origin[2]
        
        #print(self.xarr.shape)
 
        self.nx=n1
        self.ny=n2
        self.xmin=0.0
        self.ymin=0.0
        self.xmax=np.sqrt( np.sum( np.square(np.array(p1)-np.array(origin) ) ))    
        self.ymax=np.sqrt( np.sum( np.square(np.array(p2)-np.array(origin) ) ))    
        self.x_label='(cm)'
        self.y_label='(cm)'
        
    def eval_arrays(self,sss2):
        pinfos = sss2.get_positionInfo( np.reshape(self.xarr,newshape=(self.nx*self.ny,),order='C' ), 
                                        np.reshape(self.yarr,newshape=(self.nx*self.ny,),order='C' ),
                                        np.reshape(self.zarr,newshape=(self.nx*self.ny,),order='C' ) )

        pa = np.empty(shape=(len(pinfos),),dtype=object)
        for i,p in enumerate(pinfos):
            pa[i] = p

        #i = 0
        #for ix in range(self.nx):
        #    for iy in range(self.ny):
        #        a[-1].append(pinfos[i])
        #        self.pinfo_array[ix,iy] = pinfos[i]
        #        i += 1


        #pa= np.array(pinfos)
        self.pinfo_array =  np.reshape(pa,newshape=(self.nx,self.ny),order='C')
        #self.pinfo_array = a
    
    def generate_test_data(self):
        
        self.nx=500
        self.ny=580
        self.xmin= -2.0
        self.xmax=  4.0
        self.ymin=  0.0
        self.ymax=  3.0
        self.x_label="Xish (cm)"
        self.y_label="Yish (cm)"
        
        
        self.x_vec = np.linspace(self.xmin,self.xmax,self.nx)
        self.y_vec = np.linspace(self.ymin,self.ymax,self.ny)
        
        self.pinfo_array = np.empty(shape=(self.nx,self.ny),dtype=object)
        
        for ix in range(self.nx):
            for iy in range(self.ny):
                self.pinfo_array[ix,iy] = pysss2.libsss2.pinfo()
                self.pinfo_array[ix,iy].material_color_RGB[0] = int(round(ix*255/self.nx))
                self.pinfo_array[ix,iy].material_color_RGB[1] = int(round(iy*255/self.ny))
                self.pinfo_array[ix,iy].material_color_RGB[2] = int(round(np.random.uniform(low=0.0,high=255)))
    
    def get_imdata(self):
        
        # The Imdata is vertical as first index!
        imdata = np.zeros(shape=(self.ny,self.nx,3),dtype=int)
        for ix in range(self.nx):
            for iy in range(self.ny):
                imdata[iy,ix,:] = self.pinfo_array[ix,iy].material_color_RGB
        return imdata
    
    def plot(self,ax=None,fig=None):
        
        #aspect='auto'
        aspect='equal'
        


        if ax  is None:
            ax  = plt.gca()
        if fig is None:
            fig = plt.gcf()

        ai =ax.imshow(X=self.get_imdata(),aspect=aspect,origin='lower',
                        extent=(self.xmin,self.xmax,self.ymin,self.ymax) )
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        ax.set_xlim((self.xmin,self.xmax))
        ax.set_ylim((self.ymin,self.ymax))
        #plt.gca().set_aspect('equal', 'box')
        #cb=fig.colorbar()
        
        cb=self.mk_colorbar(fig)
        
        return ax,cb,ai
        