# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 08:30:08 2019

@author: Simppa Äkäslompolo, simppa.akaslompolo@alumni.aalto.fi

"""
import matplotlib.pyplot as plt
import tkinter # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
import shlex
import numpy as np

from .libsss2 import _str_encoding
from .libsss2 import sss2
import pysss2.slicer

#_LIBFILE="/homeappl/home/sjjamsa/serpent/compile_for_GUI/libsss2.so"
SERPENT="""
  _                   .-=-.           .-=-.          .-==-.       
 { }      __        .' O o '.       .' O o '.       /  -<' )--<   
 { }    .' O'.     / o .-. O \     / o .-. O \     /  .---`       
 { }   / .-. o\   /O  /   \  o\   /O  /   \  o\   /O /            
  \ `-` /   \ O`-'o  /     \  O`-'o  /     \  O`-`o /             
   `-.-`     '.____.'       `._____.'       `.____.'              

"""
PLOTTER="""


pySSS2 plotter by Simppa Äkäslompolo & Jaakko Leppänen

                  simppa.akaslompolo@alumni.aalto.fi
"""



class geom_gui(tkinter.Frame):
    
    def __init__(self,root):
        super().__init__()
        self.root = root
        self.generate_gui()
        self.selectedRectangle = (0.0, 0.0, 0.0, 0.0)

    def run_serpent(self):
        #self.btnRunSerpent['state']=tkinter.DISABLED
        self.serpentParams['state']=tkinter.DISABLED

        argv=shlex.split(self.varParams.get())
        self.varStatus.set('Initializing...Check console for output')
        self.cursor_busy()
        self.root.update()
        self._sss2 = sss2(serpent_arguments=argv)
        self.retrieveGeometryStats()
        self.varStatus.set('Serpent initialized...Check console for output')
        self.cursor_normal()
        self.root.update()

    def set_callBacks(self):
        #self.btnRunSerpent[  'command']=self.run_serpent
        #self.btnSelectRect[  'command']=self.select_rectangle
        #self.btnSetLimsSel[  'command']=self.selection_to_limits
        #self.scaleSlicer[     'command']=self.updateGeomPlotScale
        self.btnSetLimsGeom[ 'command']=self.set_limits_to_geometry
        self.btnSetLimsView[ 'command']=self.view_to_limits
        self.btnSetLimsViewU['command']=self.view_to_limits_and_update
        #self.btnUpdate['command']    =self.updateTestMatPlotLibImage
        self.btnUpdate[      'command']=self.updateGeomPlot
        self.btnSetLims11[   'command']=self.limits1to1
        self.btnSetLims110[  'command']=self.limits1to10
        self.btnGoXY[        'command']=self.to_XY_slice
        self.btnGoXZ[        'command']=self.to_XZ_slice
        self.btnGoYZ[        'command']=self.to_YZ_slice
        self.btnEvalPos[     'command']=self.eval_pos
        self.btnQuit[        'command']=self.quit
        self.btnReload[      'command']=self.reload
        self.varType.trace('w',self.set_Slicer_limits_trace)

        self.scaleSlicer.bind('<ButtonRelease-1>',self.updateGeomPlotKey)

        for entry in [self.entrySlice, 
                      self.entryMin1,  self.entryMin2, 
                      self.entryMax1,  self.entryMax2,
                      self.entryMin1,  self.entryMin2,
                      self.entryNpix1, self.entryNpix2]:
            entry.bind('<Return>',self.updateGeomPlotKey )
            entry.bind('<KP_Enter>',self.updateGeomPlotKey )
        
    def updateGeomPlotKey(self,event):
        self.updateGeomPlot()

    def updateGeomPlotScale(self,value):
        #print(value)
        self.updateGeomPlot()

    def limits1to1(self):
        self.limits1ton(1)

    def limits1to10(self):
        self.limits1ton(10)

    def limits1ton(self,n=None):
        self.view_to_limits()
        width,height = self.get_axis_size()
        if n is not None:
            width  /=  n
            height /=  n
        self.varnPix1.set("{:d}".format(int(round(width ))))
        self.varnPix2.set("{:d}".format(int(round(height))))
        self.updateGeomPlot()

    def view_to_limits_and_update(self):
        self.view_to_limits()
        self.updateGeomPlot()

    def get_axis_size(self):
        bbox = self.MatPlotAx.get_window_extent().transformed(self.MatPlotFig.dpi_scale_trans.inverted())
        width, height = bbox.width, bbox.height
        width  *= self.MatPlotFig.dpi
        height *= self.MatPlotFig.dpi
        #print('Axis size {}x{}'.format(np.round(width),np.round(height)))
        return np.round(width),np.round(height)

    def view_to_limits(self):
        xlims = self.MatPlotAx.get_xlim()
        ylims = self.MatPlotAx.get_ylim()
        
        self.varMin1.set(str(xlims[0]))
        self.varMax1.set(str(xlims[1]))
        self.varMin2.set(str(ylims[0]))
        self.varMax2.set(str(ylims[1]))


    def getParams(self):
        min1 = float(self.varMin1.get() )
        max1 = float(self.varMax1.get() )
        min2 = float(self.varMin2.get() )
        max2 = float(self.varMax2.get() )
        nPix1= int(  self.varnPix1.get())
        nPix2= int(  self.varnPix2.get())
        coord= float(self.varSlice.get())
        typ  =       self.varType.get()   


        if typ=='xy': 
            xlabel = 'x'
            ylabel = 'y'
            zlabel = 'z'
            typ = 3
        elif typ=='xz':
            xlabel = 'x'
            ylabel = 'z'
            zlabel = 'y'
            typ = 2
        elif typ=='yz':
            xlabel = 'y'
            ylabel = 'z'
            zlabel = 'x'
            typ = 1
        else:
            raise RuntimeError('Unexpected type of plot!')

        return min1,max1,min2,max2,nPix1,nPix2,coord,typ,xlabel,ylabel,zlabel

    def generate_gui(self):
        
        #self.pack(fill=tkinter.BOTH, expand=True)
        
        #from collections import namedtuple
        
        self.statusBarWidth=70
        borderThickness=1
        minMaxWidth=8
        separatorPadding=3
        
        self.varType  =tkinter.StringVar(self.root,'xy')
        self.varSlice =tkinter.StringVar(self.root,'0.0')
        self.varMin1  =tkinter.StringVar(self.root,'-1000.0')
        self.varMin2  =tkinter.StringVar(self.root,'-1000.0')
        self.varnPix1 =tkinter.StringVar(self.root,'150')
        self.varMax1  =tkinter.StringVar(self.root,'1000.0')
        self.varMax2  =tkinter.StringVar(self.root,'1000.0')
        self.varnPix2 =tkinter.StringVar(self.root,'200')
        self.varParams=tkinter.StringVar(self.root,'-interactiveplotter <inputfilename>')
        self.varStatus=tkinter.StringVar(self.root,'status')

        self.types = {'xy','xz','yz'}
        
        # This frame contains the input for coordinates etc. of the plot
        self.frameTop    = tkinter.Frame(self.root)
        self.frameTypeLoc= tkinter.Frame(self.frameTop, border=borderThickness, relief=tkinter.GROOVE)
        self.frameLimits = tkinter.Frame(self.frameTop, border=borderThickness, relief=tkinter.GROOVE)
        
        
        self.frameTop.pack(side = tkinter.TOP, expand=False, fill=tkinter.X )
        
        #
        
        # frame for type
        self.frameType   = tkinter.Frame(self.frameTypeLoc)
        self.frameSlice  = tkinter.Frame(self.frameTypeLoc)
        self.frameTypeLoc.pack(side = tkinter.LEFT, expand=False, fill=tkinter.X )

        tkinter.Label(self.frameType, text='Type', borderwidth=1).pack(side=tkinter.TOP)
        self.typeMenu = tkinter.OptionMenu(self.frameType, self.varType, *self.types)
        self.typeMenu.pack(side=tkinter.TOP)
        self.frameType.pack(side=tkinter.LEFT,fill=tkinter.X,expand=False)
        
        # frame for slice
        tkinter.Label(self.frameSlice, text='Location [cm]').pack(side=tkinter.TOP)
        self.entrySlice = tkinter.Entry(self.frameSlice, textvariable=self.varSlice, width=minMaxWidth)
        self.entrySlice.pack(side=tkinter.LEFT,expand=True,fill=tkinter.X)
        self.frameSlice.pack(side=tkinter.LEFT,fill=tkinter.X,expand=False)
        
        # frame for limits and pixels
        self.frameLimitsU = tkinter.Frame(self.frameLimits)#,bg='blue')
        self.frameLimitsL = tkinter.Frame(self.frameLimits)#,bg='gray'  )
        self.frameLimits.pack(side=tkinter.LEFT,fill=tkinter.X,expand=True)
        

        tkinter.Label(self.frameLimitsU, text='min1').pack(side=tkinter.LEFT)
        self.entryMin1 = tkinter.Entry(self.frameLimitsU, textvariable=self.varMin1, width=minMaxWidth)
        self.entryMin1.pack(side=tkinter.LEFT,expand=True,fill=tkinter.X)

        tkinter.Label(self.frameLimitsU, text='max1').pack(side=tkinter.LEFT)
        self.entryMax1 = tkinter.Entry(self.frameLimitsU, textvariable=self.varMax1, width=minMaxWidth)
        self.entryMax1.pack(side=tkinter.LEFT,expand=True,fill=tkinter.X)

        tkinter.Label(self.frameLimitsU, text='nPix1').pack(side=tkinter.LEFT)
        self.entryNpix1 = tkinter.Entry(self.frameLimitsU, textvariable=self.varnPix1, width=5)
        self.entryNpix1.pack(side=tkinter.LEFT,expand=False,fill=tkinter.X)

        self.frameLimitsU.pack(side=tkinter.TOP,expand=True,fill=tkinter.X)
        
        tkinter.Label(self.frameLimitsL, text='min2').pack(side=tkinter.LEFT)
        self.entryMin2 = tkinter.Entry(self.frameLimitsL, textvariable=self.varMin2, width=minMaxWidth)
        self.entryMin2.pack(side=tkinter.LEFT,expand=True,fill=tkinter.X)

        tkinter.Label(self.frameLimitsL, text='max2').pack(side=tkinter.LEFT)
        self.entryMax2 = tkinter.Entry(self.frameLimitsL, textvariable=self.varMax2, width=minMaxWidth)
        self.entryMax2.pack(side=tkinter.LEFT,expand=True,fill=tkinter.X)

        tkinter.Label(self.frameLimitsL, text='nPix2').pack(side=tkinter.LEFT)
        self.entryNpix2 = tkinter.Entry(self.frameLimitsL, textvariable=self.varnPix2, width=5)
        self.entryNpix2.pack(side=tkinter.LEFT,expand=False,fill=tkinter.X)

        self.frameLimitsL.pack(side=tkinter.TOP,expand=True,fill=tkinter.X)



        # The execute button
        self.btnUpdate   = tkinter.Button(self.frameTop, text='Update', state=tkinter.NORMAL, bg='green')
        self.btnUpdate.pack(side = tkinter.LEFT, expand=False, fill=tkinter.BOTH )

        
        # This frame contains the pyplot plot and the button bar
        self.frameOuterPlot          = tkinter.Frame(self.root)

        self.frameSlicer             = tkinter.Frame(self.frameOuterPlot,bg="gray", border=borderThickness, relief=tkinter.SUNKEN)
        self.frameSlicer.pack(side     = tkinter.LEFT, expand=False, fill=tkinter.Y)
        self.scaleSlicer             = tkinter.Scale(self.frameSlicer, orient=tkinter.VERTICAL, variable=self.varSlice, showvalue=False,resolution=-1.0)
        self.scaleSlicer.pack(side     = tkinter.LEFT, expand=False, fill=tkinter.Y)

        self.framePlot               = tkinter.Frame(self.frameOuterPlot)
        self.framePlot.pack(side     = tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        
        self.frameButtonBar          = tkinter.Frame(self.frameOuterPlot,bg="gray", border=borderThickness, relief=tkinter.SUNKEN)
        
        #self.btnSelectRect           = tkinter.Button(self.frameButtonBar, text='Select rectangle', state=tkinter.NORMAL); 
        #self.btnSelectRect.pack(side = tkinter.TOP, fill=tkinter.X,expand=False)
        
        #self.btnSetLimsSel           = tkinter.Button(self.frameButtonBar, text='Selection to limits', state=tkinter.DISABLED)
        #self.btnSetLimsSel.pack(side = tkinter.TOP, fill=tkinter.X, expand=False)
        self.btnSetLimsGeom= tkinter.Button(self.frameButtonBar, text='Geom. Limits', state=tkinter.NORMAL)
        self.btnSetLimsGeom.pack(side = tkinter.TOP, fill=tkinter.X, expand=False)

        self.btnSetLimsView          = tkinter.Button(self.frameButtonBar, text='View to limits', state=tkinter.NORMAL)
        self.btnSetLimsView.pack(side = tkinter.TOP, fill=tkinter.X, expand=False)

        self.btnSetLimsViewU           = tkinter.Button(self.frameButtonBar, text='View to limits & Upd', state=tkinter.NORMAL, bg='green')
        self.btnSetLimsViewU.pack(side = tkinter.TOP, fill=tkinter.X, expand=False, pady=(separatorPadding, 0))
        
        self.btnSetLims11           = tkinter.Button(self.frameButtonBar, text='V2L & P1:1 & Upd', state=tkinter.NORMAL, bg='green')
        self.btnSetLims11.pack(side = tkinter.TOP, fill=tkinter.X, expand=False)
        
        self.btnSetLims110           = tkinter.Button(self.frameButtonBar, text='V2L & P1:10 & Upd', state=tkinter.NORMAL, bg='green')
        self.btnSetLims110.pack(side = tkinter.TOP, fill=tkinter.X, expand=False)

        self.btnGoXY                = tkinter.Button(self.frameButtonBar, text='to XY & Upd', state=tkinter.NORMAL, bg='yellow')
        self.btnGoXY.pack(side = tkinter.TOP, fill=tkinter.X, expand=False, pady=(separatorPadding, 0))
        self.btnGoXZ                = tkinter.Button(self.frameButtonBar, text='to XZ & Upd', state=tkinter.NORMAL, bg='yellow')
        self.btnGoXZ.pack(side = tkinter.TOP, fill=tkinter.X, expand=False)
        self.btnGoYZ                = tkinter.Button(self.frameButtonBar, text='to YZ & Upd', state=tkinter.NORMAL, bg='yellow')
        self.btnGoYZ.pack(side = tkinter.TOP, fill=tkinter.X, expand=False)

        self.btnEvalPos                = tkinter.Button(self.frameButtonBar, text='eval pos', state=tkinter.NORMAL, bg='light sky blue')
        self.btnEvalPos.pack(side = tkinter.TOP, fill=tkinter.X, expand=False, pady=(separatorPadding, 0))
        


        self.btnQuit                 = tkinter.Button(self.frameButtonBar, text='Quit', state=tkinter.NORMAL, bg='red')
        self.btnQuit.pack(side       = tkinter.BOTTOM, fill=tkinter.X, expand=False)#, fill=tkinter.BOTH )
        
        self.btnReload               = tkinter.Button(self.frameButtonBar, text='Reload', state=tkinter.NORMAL, bg='red')
        self.btnReload.pack(side     = tkinter.BOTTOM, fill=tkinter.X, expand=False)#, fill=tkinter.BOTH )

        
        self.frameButtonBar.pack(side = tkinter.LEFT, expand=False, fill=tkinter.Y)
        self.frameOuterPlot.pack(side = tkinter.TOP, expand=True, fill=tkinter.BOTH  )
        #tkinter.Label(self.framePlot, text='plot').pack(side=tkinter.LEFT)
        
        # This frame contains the run parameters and status bar
        self.frameBottom    = tkinter.Frame(self.root, border=borderThickness, relief=tkinter.GROOVE)#,bg="blue")
        self.frameBottom.pack(side = tkinter.BOTTOM , expand=False, fill=tkinter.X)

        #tkinter.Label(self.frameBottom, text='Serpent parameters').pack(side=tkinter.LEFT)
        self.serpentParams = tkinter.Entry(self.frameBottom, textvariable=self.varParams,bg='yellow')
        self.serpentParams.pack(side=tkinter.LEFT,expand=True,fill=tkinter.X)

        #self.btnRunSerpent   = tkinter.Button(self.frameBottom, text='run')
        #self.btnRunSerpent.pack(side = tkinter.LEFT, expand=False, fill=tkinter.BOTH )

        self.statusBar     = tkinter.Label(self.frameBottom, textvariable=self.varStatus,relief=tkinter.SUNKEN,width=self.statusBarWidth).pack(side=tkinter.RIGHT)
        
        

    def to_XY_slice(self):
        self.varStatus.set('Choose the new z-value [to xy]')
        self.clickCallBackFun = self.to_XY_slice_exec
        self.to_XYZ_slice('xy')

    def to_XZ_slice(self):
        self.varStatus.set('Choose the new y-value [to xz]')
        self.clickCallBackFun = self.to_XZ_slice_exec
        self.to_XYZ_slice('xz')

    def to_YZ_slice(self):
        self.varStatus.set('Choose the new x-value [to yz]')
        self.clickCallBackFun = self.to_YZ_slice_exec
        self.to_XYZ_slice('yz')

    def eval_pos(self):
        self.varStatus.set('Click to eval geom. at location')
        self.clickCallBackFun = self.eval_pos_exec
        
    def eval_pos_exec(self,event):
        
        currType = self.varType.get()
        d = float( self.varSlice.get() )

        if currType == 'xy':
            x = event.xdata
            y = event.ydata
            z = d
            
        elif currType == 'yz':
            x = d
            y = event.xdata
            z = event.ydata

        if currType == 'xz':
            x = event.xdata
            y = d
            z = event.ydata

        self.varStatus.set( "Evaluating cell/univ/mat at (x,y,z)=({},{},{})".format(x,y,z))
        
        pinfo=self._sss2.get_positionInfo([x],[y],[z])

        self.varStatus.set( 
            "U{}:{} C{}:{} M{}:{}".format(
                pinfo[0].universe,pinfo[0].universe_name.decode(_str_encoding),
                pinfo[0].cell,    pinfo[0].cell_name.decode(    _str_encoding),
                pinfo[0].material,pinfo[0].material_name.decode(_str_encoding)  )
            )
             
        print (pinfo[0])

    def to_XYZ_slice(self,toSlice):

        from matplotlib.widgets import MultiCursor
        
        ''' 
        1) set MatPLotlibCursor correctly
        2) collect the next click
        3) (Perhaps reset the cursor)
        4) set the variables
        5) Update the plot
        '''
        
        self.MatPlotMultiCursor = None

        currType = self.varType.get()
        if currType == toSlice:
            self.varStatus.set('Already on {}-plane.'.format(toSlice))
            return


        hor,ver = self.toXYZ_horOrVer(toSlice,currType)


        #print('Hor:',hor,' Ver:',ver)
        self.MatPlotMultiCursor = MultiCursor(self.MatPlotFig.canvas, (self.MatPlotAx,), color='k', lw=1,
                    horizOn=hor, vertOn=ver)


    def toXYZ_horOrVer(self,toSlice,currType):

        hor=False
        ver=False

        # Horizontal or vertical bar?
        if toSlice=='xy':
            if currType == 'xz':
                #choose z (vert axis, line hor) 
                hor=True
            if currType == 'yz':
                #choose z (vert axis, line hor) 
                hor=True
        elif toSlice=='xz':
            if currType == 'xy':
                #choose y (vert axis, line hor) 
                hor=True
            if currType == 'yz':
                #choose y (hor  axis, line ver) 
                ver=True
        elif toSlice=='yz':
            if currType == 'xy':
                #choose x (hor  axis, line ver) 
                ver=True
            if currType == 'xz':
                #choose x (hor  axis, line ver) 
                ver=True

        else:
            raise ValueError('Unexpected toSlice "'+str(toSlice)+'"')

        return hor,ver


    def to_XY_slice_exec(self,event):
        self.to_XYZ_slice_exec('xy',event)

    def to_XZ_slice_exec(self,event):
        self.to_XYZ_slice_exec('xz',event)

    def to_YZ_slice_exec(self,event):
        self.to_XYZ_slice_exec('yz',event)

    def to_XYZ_slice_exec(self,toSlice,event):
        self.MatPlotMultiCursor = None
        self.clickCallBackFun = None

        if not ( toSlice == 'xy' or  toSlice == 'xz' or  toSlice == 'yz'):
            raise ValueError('Unexpected toSlice "'+str(toSlice)+'"')


        currType = self.varType.get()
        self.varType.set(toSlice)

        centre=float(self.varSlice.get())
        if (  (toSlice == 'xy' and currType == 'yz' )    ):
            # the 2nd dimension information is used, swap
            width = float(self.varMax2.get())-float(self.varMin2.get())
            self.varMin1.set( self.varMin2.get() )
            self.varMax1.set( self.varMax2.get() )
            self.varMin2.set( str( centre-width/2) )
            self.varMax2.set( str( centre+width/2) )
        elif ((toSlice == 'yz' and currType == 'xy' )    ):
            # the 1st dimension information is used, swap
            width = float(self.varMax1.get())-float(self.varMin1.get())
            self.varMin1.set( str( centre-width/2) )
            self.varMax1.set( str( centre+width/2) )
            self.varMin2.set( self.varMin1.get() )
            self.varMax2.set( self.varMax1.get() )
        elif( (toSlice == 'xy' and currType == 'xz' ) or
              (toSlice == 'xz' and currType == 'xy' )    ):
            # the 1st dimension information is used
            width = float(self.varMax1.get())-float(self.varMin1.get())
            self.varMin2.set( str( centre-width/2) )
            self.varMax2.set( str( centre+width/2) )
        elif( (toSlice == 'xz' and currType == 'yz' ) or
              (toSlice == 'yz' and currType == 'xz' )    ):
            # the 2nd dimension information is used
            width = float(self.varMax2.get())-float(self.varMin2.get())
            self.varMin1.set( str( centre-width/2) )
            self.varMax1.set( str( centre+width/2) )
        else:
            raise ValueError('Unexpected toSlice "'+str(toSlice)+'" with currType "'+str(currType)+'"')

        hor,ver = self.toXYZ_horOrVer(toSlice,currType)
        if hor and ver:
            raise ValueError('Both horizontal and vertical?')
        elif hor:
            self.varSlice.set(event.ydata)
        elif ver:
            self.varSlice.set(event.xdata)
        else:
            raise ValueError('Not horizontal nor vertical?')

        self.root.update()
        self.updateGeomPlot()

    def generate_colormap(self,rgb):
        ''' rgb should be Nx3 numpy array'''

        from matplotlib.colors import ListedColormap
        
        # We need an Nx4 numpy array
        n = rgb.shape[0]
        #print(rgb.shape)
        oness=np.ones( (n,1) )
        #print(oness.shape)
           
        arr = np.concatenate( (rgb.T,oness.T  ) ).T
        

        cm = ListedColormap(arr)  
        return cm

    def updateGeomPlot(self):
        self.varStatus.set("Updating from Serpent...")
        self.cursor_busy()
        self.root.update()

        
        currType = self.varType.get()

        self.set_Slicer_limits()

        min1,max1,min2,max2,nPix1,nPix2,coord,typ,xlabel,ylabel,zlabel = self.getParams()
        nx=nPix1
        ny=nPix2

        S=pysss2.slicer.cartesian_plotter()
        S.from_cartesian(nx,ny,cut_type=currType,
                         min1=min1, max1=max1,
                         min2=min2, max2=max2,
                         d3=coord);
        S.eval_arrays(self._sss2);
        
        self.MatPlotFig.clear()
        self.MatPlotAx = self.MatPlotFig.add_subplot(111)

        _,self.MatPlotColorbar,self.MatPlotAxesImage=S.plot(ax=self.MatPlotAx,fig=self.MatPlotFig)

 
        self.MatPlotCanvas.draw()

        self.varStatus.set("Ready.")
        self.cursor_normal()
        self.root.update()





    def makeFigure(self):
        #https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
        from matplotlib.backends.backend_tkagg import (
                FigureCanvasTkAgg, NavigationToolbar2Tk)
        from matplotlib.figure import Figure
        #import matplotlib.colorbar 
        from matplotlib import cm

        fig = Figure(figsize=(5,4),dpi=100)


        ax = fig.add_subplot(111)

        splash = ax.text(0,0, SERPENT+PLOTTER)
        splash.set_fontfamily('monospace')
        ax.axis("off")


        canvas = FigureCanvasTkAgg(fig, master=self.framePlot)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        #https://stackoverflow.com/questions/26064465/using-matplotlibs-ginput-function-with-tkinter-gui
        #self.bind("<Button-1>",self.showXY_handler)
        
        
     

        
        toolbar = NavigationToolbar2Tk(canvas, self.framePlot)
        toolbar.update()
        
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)


        #self.MatPlotAxesImage = ai
        self.MatPlotCanvas  = canvas
        self.MatPlotToolbar = toolbar
        #self.MatPlotAx      = ax
        self.MatPlotFig     = fig
        #self.nColors        = nColors
        #self.MatPlotColorbar= cb

        #self.select_rectangle_create()

        #canvas.mpl_connect("key_press_event", self.on_mpl_key_press)
        canvas.callbacks.connect('button_press_event', self.showXY_handler)


    def selection_to_limits(self):
        self.varMin1.set(str(self.selectedRectangle[0]))
        self.varMax1.set(str(self.selectedRectangle[1]))
        self.varMin2.set(str(self.selectedRectangle[2]))
        self.varMax2.set(str(self.selectedRectangle[3]))
        #size = self.MatPlotFig.get_size_inches() * self.MatPlotFig.dpi
        #print(size)
        self.removeSelectionRectangle()

    def removeSelectionRectangle(self):
        # https://github.com/matplotlib/matplotlib/issues/12420/
        #self.selectionRectangle.active=False
        #del(self.selectionRectangle)
        #print('Removing')
        #self.selectionRectangle.remove()
        self.selectionRectangle.set_visible(False)
        self.MatPlotCanvas.draw()
        self.btnSetLimsSel['state']=tkinter.DISABLED
        self.btnSelectRect['state']=tkinter.NORMAL

    def on_mpl_key_press(self,event):
        # Implement the default Matplotlib key bindings.
        from matplotlib.backend_bases import key_press_handler

        print("you pressed {}".format(event.key))
        key_press_handler(event, self.MatPlotCanvas, self.MatPlotToolbar)


    def line_select_callback(self,eclick, erelease):
        # https://matplotlib.org/examples/widgets/rectangle_selector.html
        'eclick and erelease are the press and release events'

        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        #print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        #print(" The button you used were: %s %s" % (eclick.button, erelease.button))
        #if str(erelease.button) == "MouseButton.RIGHT" or str(eclick.button) == "MouseButton.RIGHT" :
        #    print('Right button => attempt to delete the widget')
        #    print('Now would be the time to store the coordinates!',(x1, y1, x2, y2))
        self.varStatus.set("Selection: ({:12f} -- {:12f}, {:12f} -- {:12f})".format(x1,x2,y1,y2))
        self.selectedRectangle = (x1, x2, y1, y2)
        #    self.selectionRectangle.set_active(False)
        #    del(self.selectionRectangle)
            #self.MatPlotAx.draw()
            #self.root.update()
        #    self.MatPlotCanvas.draw()

    def select_rectangle(self):
        # The final selection goes to self.selectedRectangle

        self.varStatus.set("Click-and-drag a rectangle")

        # https://matplotlib.org/examples/widgets/rectangle_selector.html
        self.selectionRectangle.set_visible(True)
        self.selectionRectangle.active=True
        self.btnSetLimsSel['state']=tkinter.NORMAL
        self.btnSelectRect['state']=tkinter.DISABLED


    def select_rectangle_create(self):


        import matplotlib.widgets
        
        usingBlit = False

        self.selectionRectangle = matplotlib.widgets.RectangleSelector(self.MatPlotAx, self.line_select_callback,
                                       drawtype='box', useblit=usingBlit,
                                       button=[1, 3],  # don't use middle button
                                       minspanx=5, minspany=5,
                                       spancoords='pixels',
                                       interactive=True)
        #print('SELECTION ENDED')
        self.selectionRectangle.set_visible(False)
        self.selectionRectangle.active=False





    def showXY_handler( self,  event ):
        #https://stackoverflow.com/questions/27565939/getting-the-location-of-a-mouse-click-in-matplotlib-using-tkinter
        if event.inaxes is not None:
            print('Click coordinates: ',event.xdata, event.ydata)
            
            if hasattr(self,'clickCallBackFun'):
                if self.clickCallBackFun is not None:
                    self.clickCallBackFun(event)

        else:
            print('Clicked outside axes bounds but inside plot window')

    def show_error(self, *args):

        ''' Too difficult! We ignore everything because we can't figure out how to check for the error message!
        '''
        
        #if not args[2] == "'FigureCanvasTkAgg' object has no attribute 'manager'":
        #    raise #args[0],args[1],args[2]
        #else:
        #    print(args[2])
        #import traceback
        #import pdb
        #err = traceback.format_exception(*args)
        #print('<<')
        #print(*args)
        #print(err)
        #print('>>')
        #pdb.set_trace()
        pass
  
            
    def quit(self):
        plt.close('all')
        self.root.destroy()

    def reload(self): 
        self.varStatus.set('Attempting to reload.')
        self.root.update()
        #plt.close('all')

        result= self._sss2.sss2_free()
        
        self.varStatus.set('FreeMem() completed (status {})'.format(result))
        
        self.run_serpent()
        
        # restart_old()


    def get_frames_for_cursor(self):
        w=[self.frameOuterPlot,self.frameTop,self.frameBottom]
        return w

    def cursor_busy(self):
        for w in self.get_frames_for_cursor():
            w['cursor']='clock'

    def cursor_normal(self):
        for w in self.get_frames_for_cursor():
            w['cursor']=''

    def retrieveGeometryStats(self):
        self.geom_stats = self._sss2.getGeometryParameters()
        self.set_limits_to_geometry()

    def set_limits_to_geometry(self):

        T= self.varType.get() 
        if   T == 'xy':
            self.varMin1.set(str(self.geom_stats.xmin))
            self.varMax1.set(str(self.geom_stats.xmax))
            self.varMin2.set(str(self.geom_stats.ymin))
            self.varMax2.set(str(self.geom_stats.ymax))
        elif T == 'xz':
            self.varMin1.set(str(self.geom_stats.xmin))
            self.varMax1.set(str(self.geom_stats.xmax))
            self.varMin2.set(str(self.geom_stats.zmin))
            self.varMax2.set(str(self.geom_stats.zmax))
        elif T == 'yz':
            self.varMin1.set(str(self.geom_stats.ymin))
            self.varMax1.set(str(self.geom_stats.ymax))
            self.varMin2.set(str(self.geom_stats.zmin))
            self.varMax2.set(str(self.geom_stats.zmax))
        else:
            raise ValueError('Unexpected varType: "{}"'.format(T))

        self.set_Slicer_limits()
        #print('Zminmax',self.geom_stats.zmin,self.geom_stats.zmax)

    def set_Slicer_limits_trace(self,arg1,arg2,arg3):
        #print(arg1)
        #print(arg2)
        #print(arg3)
        self.set_Slicer_limits()

    def set_Slicer_limits(self):

        T= self.varType.get() 
        if   T == 'xy':
            self.scaleSlicer.config(to=   self.geom_stats.zmin)
            self.scaleSlicer.config(from_=self.geom_stats.zmax)
        elif T == 'xz':
            self.scaleSlicer.config(to=   self.geom_stats.ymin)
            self.scaleSlicer.config(from_=self.geom_stats.ymax)
        elif T == 'yz':
            self.scaleSlicer.config(to=   self.geom_stats.xmin)
            self.scaleSlicer.config(from_=self.geom_stats.xmax)
        else:
            raise ValueError('Unexpected varType: "{}"'.format(T))

    def set_parameters(self,args):
        string = ""
        for a in args:
            if ' ' in a:
                string = string + '"' + a+'" '
            else:
                string = string +  a + ' '
        self.varParams.set(string)

        
def test():
    root = tkinter.Tk()
    root.wm_title('SSS2 plotting')
    G=geom_gui(root)
    G.set_callBacks()
    #G.makeTestMatPlotLibPlot(G.framePlot)
    G.makeTestMatPlotLibImage(G.framePlot)
    # There is a bug in matplotlib 3.1.0 (should be fixed in 3.1.1 )
    # https://github.com/matplotlib/matplotlib/issues/14781
    # We can suppress the errors, but save probably will still not work.
    #tkinter.Tk.report_callback_exception = G.show_error
    #G.MatPlotToolbar.report_callback_exception = G.show_error
        
    

    root.mainloop()


def GUI(sss2_args=None,libfile=None):
    print('..TK init..')
    root = tkinter.Tk()
    root.wm_title('SSS2 plotting')
    print('..GUI init..')
    G=geom_gui(root)
    G.set_callBacks()
    #print('..Test image..')
    #G.makeTestMatPlotLibImage(G.framePlot)
    print('..MatPlotLib Figure..')
    G.makeFigure()

    if sss2_args is not None:
        print('..starting Serpent..')
        #G.btnRunSerpent['state']=tkinter.DISABLED
        G.serpentParams['state']=tkinter.DISABLED
        G.set_parameters(sss2_args)
        G.varStatus.set('Initializing...Check console for output')
        G.cursor_busy()
        G.root.update()
        G._sss2 = sss2(serpent_arguments=sss2_args,libfile=libfile)
        G.retrieveGeometryStats()
        G.varStatus.set('Serpent initialized...Check console for output')
        G.cursor_normal()

        G.updateGeomPlot()

        G.root.update()
    else:
        print('..Message..')
        tkinter.messagebox.showinfo("pySSS2", "Start by inputting serpent command line in the bottom. This could be done already on command line.")

    print('..main loop commencing..')
    root.mainloop()
    

def restart_old():
    """Restarts the current program, with file objects and descriptors
        cleanup
    From: https://stackoverflow.com/questions/11329917/restart-python-script-from-within-itself
        """
 
 
    import os
    import sys
    import psutil
    import logging
 
    print('Attempting to restart the program')
     
    try:
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e) 

    print('    ...now.')
    python = sys.executable
    os.execl(python, python, *sys.argv)
     

