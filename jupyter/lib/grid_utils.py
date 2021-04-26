import numpy as np

def array_to_ESRIascii(data, 
                       file="./grid.asc", 
                       cellsize=1, 
                       llcenter=[0,0], 
                       nodatavalue=-1e-6,
                       reverse_array=True):
    """Converts a 2-D array into an ESRI ascii grid format file.
    
    Parameters:
    -----------
    data:           2-D array-like of grid data
    
    file:           filename name where grid will be saved
    
    cellsize:       cell size
    
    llcenter:       (x, y) coordinates of center of lower left cell
    
    nodatavalue:    value used to represent no data, will be 
                    substituted for any Null/np.nan values in data
                    
    reverse_array:  if True, reverse sort data rows - see Note 2 below
    
    Notes:
    ------
    1. There is no boiler plating for file name. Caution is needed to 
    avoid overwriting existig files etc.
    
    2. ESRI ascii files take data with top row first. It is likely
    the array supplied to 'data' parameter is top row last. Use the
    'reverse_array' parameter to reverse input data as needed.
    """
    
    data = np.asarray(data)
    if reverse_array:
        data = data[::-1]
    rows, cols = data.shape

        
    with open(file, 'w') as outfile:
            
        outfile.write("NCOLS {}\n".format(cols))
        outfile.write("NROWS {}\n".format(rows))
        outfile.write("XLLCENTER {}\n".format(llcenter[0]))
        outfile.write("YLLCENTER {}\n".format(llcenter[1]))
        outfile.write("CELLSIZE {}\n".format(cellsize))
        outfile.write("NODATA_VALUE {}\n".format(nodatavalue))
            
        data = np.where(np.isnan(data), nodatavalue, data)
        data = np.array2string(data, threshold=rows * cols)
        data = (data.replace('[','').replace(']','')
                .replace('\n ', '\n'))
        outfile.write(data)
