from math import pi, cos, sin

import numpy as np


def spherical_semivariogram(x, az, rng, sill, nugget=0):
    """Returns the semivariance for the lag vectors x using 
    a 2D ellitical anisotropic spherical semivariogram.
    
    Parameters:
    ----------
    x:      array like, at least 2D
            array of lag vectors
            
    az:     scalar
            azimuth in degrees of the semi-major axis of the semivariogram.
            
    rng:    2 element list like
            semi-major and semi-minor ranges of the semivariogram in 
            same units as x1 and x2.
            
    sill:   scalar
            sill of the semivariogram.
            
    nugget: scalar
            nugget of the semivariogram.
            
            
    Returns:
    --------
    ndarray of semivariance values.
    
    Notes:
    ------
    Lag vector length is calculated in a Euclidean space.
    """
    
    # get lag vector coordinates
    h = np.asarray(x)
    
    # affine rotation of lag vectors 
    # convert azimuth to radians with origin along x axis first!
    t = az/180 * pi + pi/2
    Q = np.array([[cos(t), sin(t)], 
                  [-sin(t), cos(t)]])
    h = np.matmul(h, Q)
    
    # affine scaling of lag vectors to match anisotropy
    r = rng[0] / rng[1]
    D = np.array([[1, 0], 
                  [0, r]])
    h = np.matmul(h, D)
    
    # get Euclidean length of lag vectors
    h = (h ** 2).sum(axis=-1) ** 0.5
    
    # return semivariances
    return np.where(h < rng[0], 
                    ((sill - nugget) * 
                     (3 * h / 2 / rng[0] - 0.5 * np.power(h / rng[0], 3)) + 
                     nugget),
                    sill)
