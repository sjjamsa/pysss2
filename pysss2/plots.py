from matplotlib.colors import ListedColormap
import numpy as np
import matplotlib.pyplot as plt

    
    
def generate_colormap(rgb):
    ''' rgb should be Nx3 numpy array
    with values in range 0...1
    '''

    
    
    # We need an Nx4 numpy array
    n = rgb.shape[0]
    #print(rgb.shape)
    oness=np.ones( (n,1) )
    #print(oness.shape)
       
    arr = np.concatenate( (rgb.T,oness.T  ) ).T
    

    cm = ListedColormap(arr)  
    return cm


def plot_indexed_image(arr,rgb, min1,max1,min2,max2,xlabel='',ylabel='',axis=None, **kwargs):
    
    # Generate the colormap
    nColors = arr.max()
    cm = generate_colormap( rgb[:nColors,:]/255.0 )
    clim=(-0.5,nColors-0.5)
    
    # Create new axis, if not given as a parameter
    if axis is None:
        ax = plt.subplot(111)
    else:
        ax = axis
    
        
    # Do the actual plotting 
    ai = ax.imshow(arr, extent=(min1, max1, min2, max2),cmap=cm,vmin=clim[0],vmax=clim[1],**kwargs)
    
    

        
        
    # Add labels etc.
    ax.set_xlabel(xlabel+" (cm)")
    ax.set_ylabel(ylabel+" (cm)")
    ax.set_xlim( (min1, max1) )
    ax.set_ylim( (min2, max2) )
    ax.set_aspect('equal')
        
    return ai,ax