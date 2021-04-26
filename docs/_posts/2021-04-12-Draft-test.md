---
layout: post
draft: false
title:  "Simple Kriging in 5 lines of Python or less..."
tags: python geostatistics kriging variogram
image: net.png
notebook: 1-limestone-hatch
---


...or "look ma', no for loops!"

I like this example as it demonstrates the brutal efficiency of Python coding without compromising on performance thanks to NumPy's vectorized functions. While there are a few extra lines to set things up, the actually kriging algorithm itself really is only 4-5 lines of code.

<!--more-->

This article is not an in-depth explanation of the kriging estimator, its pros and cons, or how it might be relevant to this or that geological application. The goal here is to provide insight in to creating an efficient kriging algorithm in Python. It does not cover the topics of spatial correlation or semivariance either; we assume here that the experimental semivariogram is known and that an appropriate model semivariogram has been selected. Finally, we assume the reader has some familiarity with NumPy's [broadcasting principles](https://numpy.org/doc/stable/user/basics.broadcasting.html).



## Theoretical background

Before we get started, a little refresher of how Simple Kriging works is in order. 

Kriging is a basic statistical linear estimator. A property's value *&#7825;* in location *o*, can be estimated  based on known values *z<sub>i</sub>*, *i=1,...I* as:


{% include equation.html file="images/posts/article-2/Equation_1.png"
alt="equation 1" number="1" height="60" %}

where *&lambda;<sub>i</sub>* is the kriging weight for known point *z<sub>i</sub>*. The kriging weights for an observation point *o* can be determined by minimizing the Simple Kriging (SK) variance defined as:

{% include equation.html file="images/posts/article-2/Equation_2.png"
alt="equation 2" number="2" height="30" %}

where *z* is the true, but unknown, value of our property at point *o* and *E* is the expectation. From an analytical perspective, this is achieved by seeking appropriate kriging weights such that the first derivative of the Simple Kriging variance is equal to zero. This has the advantage of removing the actual value *z* from the equation &mdash; pun intended, and allows us to find the weights without this knowledge. *The reader is referred to an appropriate text (e.g., Jensen et al., 2003) for the full workings out and the assumptions made.* To cut things short, the kriging weights can be found by solving the matrix equation:

{% include equation.html file="images/posts/article-2/Equation_3.png"
alt="equation 3" number="3" height="79" %}

where *&sigma;<sub>ij</sub><sup>2</sup>* is the covariance between known points *z<sub>i</sub>* and 
*z<sub>j</sub>*, and *&sigma;<sub>oi</sub><sup>2</sup>* is the covariance between unknown point *z<sub>o</sub>* and known point *z<sub>i</sub>*. Given the simplifications resulting from the stationarity assumptions *not* discussed above, the covariance between points can be determined using their semivariance as:

{% include equation.html file="images/posts/article-2/Equation_4.png"
alt="equation 4" number="4" height="31" %}

where *&sigma;<sup>2</sup>(x<sub>i</sub>, x<sub>j</sub>)* is the covariance between *x<sub>i</sub>* and *x<sub>j</sub>*, *h* is the lag distance or lag between these 2 points, *&gamma;* is the semivariance, and *&sigma;<sup>2</sup>* is the sample variance.

For simplicity, we can rewrite equation (3) in vector notation as:

{% include equation.html file="images/posts/article-2/Equation_5.png"
alt="equation 5" number="5" height="30" %}

Once we have solved Equation (5) for *&Lambda;*, we can estimate the value of *Z* at all points on a *(x, y)* grid of *M* points:

{% include equation.html file="images/posts/article-2/Equation_6.png"
alt="equation 6" number="6" height="26" %}

where *&#7824;* is an *M*-element vector of estimated values, *Z* is an *I*-element of known values, and *&Lambda;<sup>T</sup>* is an *I* x *M* matrix of kriging weights. The corresponding Simple Kriging variance (or error in the estimation) is determined by:

{% include equation.html file="images/posts/article-2/Equation_7.png"
alt="equation 7" number="7" height="30" %}

## Simple Kriging

### Import necessary libraries

```python
from math import pi, cos, sin

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, FuncFormatter
import numpy as np

from lib.semivariograms import spherical_semivariogram
```

The `spherical_semivariogram` function is an implementation of a 2D anisotropic spherical semivariogram taking as arguments the coordinates of lag vectors and the semivariogram's semi-major & semi-minor ranges, azimuth, sill and nugget. It returns the corresponding semivariance for the lags defined by the lag vectors, including their orientations. For now, you can get a copy of the library [here](https://github.com/dlodola/public/tree/main/jupyter/lib), but I will cover it in more detail in a future article.

### Set up grid

First lets create a (*I*, *J*, *2*) array `grid` such that each [*i*, *j*] node holds
the (*x<sub>i</sub>*, *y<sub>j</sub>*) Cartesian coordinates of that node. It is set up using the (*x<sub>0</sub>*, *y<sub>0</sub>*) coordinates of the lower left corner, the cell size and the number of rows and columns.

<!--
{% include equation.html file="images/posts/article-2/Equation_8.png"
alt="equation 8" number="8" height="79" %}


Going forward, we will mostly work with a part flattened copy of `grid` with dimensions (*M*, *2*), where the first dimension holds all the nodes and the second holds the nodes (*x*, *y*) coordinates. By convention:

1. M is the number of nodes in the grid where property is estimated (*i.i*, rows * columns).
2. m: a node with in grid with coordinates (*x*, *y*).
3. I: the number of known points for the property.
4. i: a known point with coordinates (*x<sub>i</sub>*,*y<sub>i</sub>*). -->

```python
LL_CENTER = (1_000_000, 500_000)
CELL_SIZE = 50
ROWS, COLS = 300, 400

nodes = ROWS * COLS

# list of all column (x) coordinates
xx = np.arange(LL_CENTER[0], 
               LL_CENTER[0] + COLS * CELL_SIZE, 
               CELL_SIZE)

# list of all row (y) coordinates
yy = np.arange(LL_CENTER[1], 
               LL_CENTER[1] + ROWS * CELL_SIZE, 
               CELL_SIZE)

# (I,J,2) array where each (i,j) node is its (x,y) coordinates
grid = np.array(np.meshgrid(xx, yy)).transpose([1,2,0])
```

### Load data and create semivariogram

```python
# semi variogram parameters
NUGGET = 0                # nugget
RANGE = (3_500, 2_500)    # [major, minor] axis length in grid units
AZ = 45                   # azimuth in degrees (North = 0)

# sample variance
s2 = obs[:, -1].var()

# create lambda function for semivariance taking just lag
# vectors as arguments:
gamma = lambda x: spherical_semivariogram(x, AZ, RANGE, s2, NUGGET)
```

### Perform Simple Kriging

Now that we are all set up, we can implement our 4 lines for the Simple Kriging algorithm:

```python
# line 1
s_oi = s2 - gamma(grid[...,None,:].repeat(num_obs, axis=-2) - obs[:,:2])
# line 2
s_ij = s2 - gamma(obs[...,None,:2].repeat(num_obs, axis=-2) - obs[:,:2])
# line 3
L = np.linalg.solve(s_ij, s_oi.swapaxes(-1,-2)).swapaxes(-1,-2)
# line 4
Z_sk = np.matmul(L, obs[:,2])
# line 5
S_sk = s2 - (L * s_oi).sum(axis=2)
```

1. We apply Equation (4) to determine *&Sigma;<sub>o</sub><sup>2</sup>* used in equation (5). `grid` is repeated *K* times along a new penultimate axis &mdash; where *K* is the number of known points, from which we subtract the coordinates of the known points. This yields an (*I*, *J*, *K*, *2*) array where each element of the penultimate axis is an array of *K* vectors between grid node (*i*, *j*) and known points *k=1,...,K*. 
These are then fed to the semivariogram function `gamma`, returning an (*I*, *J*, *K*) array where each [*i*, *j*, *k*] element is the semivariance between grid node (*i*, *j*) and known point *k*. This is then subtracted from the sample variance to give the (*I*, *J*, *K*) array of covariances between all grid nodes and all known points.

2. Similarly, Equation (4) is used to determine *&Sigma;<sup>2</sup>*. This time we provide a (*K*, *K*) array of (*x<sub>k</sub>*, *y<sub>k</sub>*) coordinates for all known points to the semivariogram function.
We end up with a (*K*, *K*) array of covariances between all known points.

3. We now use NumPy's [linalg.solve](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html?highlight=solve#numpy.linalg.solve) routine to solve Equation (6) for *&Lambda;*. The last two axes of *&Sigma;<sub>o</sub><sup>2</sup>* are swapped to allow the arrays to broadcast properly and the output is swapped back to maintain the correct shape .This returns an (*I*, *J*, *K*) array where each element in the last dimension is a *K*-element vector of Simple Kriging weights *&lambda;<sub>k</sub>* for point (*x<sub>i</sub>*, *y<sub>j</sub>*).

4. We can now estimate the property value at each grid node using Equation (6) by summing the values of our known points multiplied by the Simple Kriging weights.
We end up with a (*I*, *J*) array where each [*i*, *j*] node is the estimated value for the coordinates (*x<sub>i</sub>*, *y<sub>j</sub>*).

5. Similarly, we can use Equation (7) to determine the Simple Kriging variance.

Figure 1 attempts to give a visual representation of lines 1-4, with an emphasis on array manipulations and broadcasting.

{% include image.html file="posts/article-2/figure-1.png"
alt="Figure 1" number="1" link="true" caption="Schematic representation of kriging algorithm. Bold outlines illustrate how broadcasting is applied." %}

### Display results

```python
fig, ax = plt.subplots(figsize=(12,10))

# display grid as filled contour plot and add/annotate observation data
disp = ax.contourf(grid[...,0], grid[...,1], Z_sk2, 
                   levels=10, cmap='seismic')
fig.colorbar(disp, fraction=0.025)
CS = ax.contour(grid[...,0], grid[...,1], Z_sk2, 
                levels=10, colors='k', linewidths=0.5)
ax.clabel(CS, inline=True, fmt='%.2f', zorder=2)
ax.scatter(obs[:,0], obs[:,1], fc='w', ec='k', zorder=2)
bbox = {'boxstyle':  'round4',
        'pad':       0.15,
        'facecolor': 'w',
        'edgecolor': 'k'}
for ob in obs:
    ax.annotate("{:.2f}".format(ob[2]), (ob[0]+100, ob[1]+100), 
                c='k', bbox=bbox, zorder=3)

# format ticks and set aspect ratio to 1
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
ax.tick_params(top=True, right=True)
ax.set_aspect(1)

plt.show()
```

{% include image.html file="posts/article-2/figure-2.png"
alt="Figure 2" number="2" link="true" caption="Simple Kriging output." %}


{% include image.html file="posts/article-2/figure-3.png"
alt="Figure 3" number="3" link="true" caption="Simple Kriging variance." %}

### Serialize

to ESRI ascii or [Rasterio](https://rasterio.readthedocs.io/en/latest/)

## Where next?

### Other kriging methods

Figure 4 shows the output of our Simple Kriging example alongside the outputs from the same input parameters and data using Ordinary, and First & Second Order Universal Kriging. These other kriging methods impose more constraints on the kriging weights &mdash; they must sum up to one in Ordinary Kriging for example, but can be easily implemented from the above with the appropriate modifications to the *&Sigma;<sup>2</sup>* and *&Sigma;<sub>o</sub><sup>2</sup>* arrays. 

{% include image.html file="posts/article-2/figure-4.png"
alt="Figure 4" number="4" link="true" caption="Alternative kriging methods." %}

### Limitations

Two main areas of limitation

1. Though this example is both efficient from a coding and execution time perspectives, it is inefficient from a memory perspective as NumPy's vectorization is memory hungry. 

2. No search radius limitation where covariances are poorly defined. Easily implemented? No preprocessing (declustering etc)

### Existing geostatistic implementations

[geostatspy](https://pypi.org/project/geostatspy/)

[scikit-gstat](https://pypi.org/project/scikit-gstat/)


## References

**Deutsch, C.V., &d Journel, A.G., 1997,** GSLIB Geostatistical Software Library and User’s Guide, Oxford University Press, New York, 2<sup>nd</sup> Edition, 369 pages.

**Jensen, J.L., L.W. Lake, P.W.M. Corbett, & D.J. Goggin, 2003,** Statistics for Petroleum Engineers and Geoscientists, 2<sup>nd</sup> Edition, Elsevier, 338 pages.