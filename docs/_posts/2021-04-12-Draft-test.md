---
layout: post
draft: false
title:  "Simple Kriging in 5 lines of Python or less..."
tags: python geostatistics kriging variogram
image: net.jpg
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

## Import necessary libraries and set things up

```python
from math import pi, cos, sin

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, FuncFormatter
import numpy as np

from lib.semivariograms import spherical_semivariogram
```

The `spherical_semivariogram` function is an implementation of a 2D anisotropic spherical semivariogram taking as arguments the coordinates of 2 sets of points and the semivariogram's semi-major & semi-minor ranges, azimuth, sill and nugget. It returns the corresponding semivariance for the lags between the points in both sets of inputs. For now, you can get a copy of the library [here](), but I will cover it in more detail in a future article.

### Grid

First lets create a (*i*, *j*, *k*) array `grid` such that each [*i*,*j*] node holds
the (*x<sub>i</sub>*, *y<sub>j</sub>*) Cartesian coordinates of that node. It is set up using the (*x<sub>0</sub>*, *y<sub>0</sub>*) coordinates of the lower left corner, the cell size
and the number of rows and columns.

{% include equation.html file="images/posts/article-2/Equation_8.png"
alt="equation 8" number="8" height="79" %}


Going forward, we will mostly work with a part flattened copy of `grid` with dimensions (*M*, *2*), where the first dimension holds all the nodes and the second holds the nodes (*x*, *y*) coordinates. By convention:

1. M is the number of nodes in the grid where property is estimated (*i.i*, rows * columns).
2. m: a node with in grid with coordinates (*x*, *y*).
3. I: the number of known points for the property.
4. i: a known point with coordinates (*x<sub>i</sub>*,*y<sub>i</sub>*).

```python
LL_CORNER = (1_000_000, 500_000)
CELL_SIZE = 50
ROWS, COLS = 300, 400

nodes = ROWS * COLS

# list of all column (x) coordinates
xx = np.arange(LL_CORNER[0], 
               LL_CORNER[0] + COLS * CELL_SIZE, 
               CELL_SIZE)

# list of all row (y) coordinates
yy = np.arange(LL_CORNER[1], 
               LL_CORNER[1] + ROWS * CELL_SIZE, 
               CELL_SIZE)

# (i,j,k) array where each (i,j) node is its (x,y) coordinates
grid = np.array(np.meshgrid(xx, yy)).transpose([1,2,0])
```

{% include image.html file="posts/article-2/figure-1.png"
alt="Figure 1" number="1" link="true" caption="Schematic representation of kriging algorithm." %}


[geostatspy](https://pypi.org/project/geostatspy/)

[scikit-gstat](https://pypi.org/project/scikit-gstat/)