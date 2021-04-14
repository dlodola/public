---
layout: post
draft: true
title:  "Simple Kriging 5 lines of Python or less..."
tags: python matplotlib lithologies hatch
image: net.jpg
notebook: 1-limestone-hatch
---


...or "look ma', no for loops!"

I like this example as it demonstrates the brutal efficiency of Python coding without compromising on performance thanks to NumPy's vectorized functions. While there are a few extra lines to set things up, the actually kriging algorithm itself is only 4-5 lines of code.

This article is not an in-depth explanation of the kriging estimator, its pros and cons, or how it might be relevant to this or that geological application. The goal here is to provide insight in to creating an efficient kriging algorithm in Python. It does not cover the topics of spatial correlation or semivariance either; we assume here that the experimental semivariogram is known and that an appropriate model semivariogram has been selected. Finally, we assume the reader has some familiarity with NumPy's [broadcasting principles](https://numpy.org/doc/stable/user/basics.broadcasting.html).



## Theoretical background

Before we get started, a little refresher of how Simple Kriging works is in order. 

Kriging is a basic statistical linear estimator. A property's value *&#7825;* in location *o*, can be estimated  based on known values *z<sub>i</sub>*, *i=1,...I* as:

{% include equation.html file="images/posts/article-2/Equation_1.png"
alt="equation 1" number="1" height="50" %}

where *&lambda;<sub>i</sub>* is the kriging weight for known point *z<sub>i</sub>*. The kriging weights for an observation point *o* can be determined by minimizing the Simple Kriging (SK) variance defined as:

{% include equation.html file="images/posts/article-2/Equation_2.png"
alt="equation 2" number="2" height="25" %}

where *z* is the true, but unknown, value of our property at point *o* and *E* is the expected value. From an analytical perspective, this is achieved by seeking appropriate kriging weights such that the first derivative of the Simple Kriging variance is equal to zero. This has the advantage of removing the actual value *z* from the equation &mdash; pun intended, and allows us to find the weights without this knowledge. *The reader is referred to an appropriate text (e.g., Jensen et al., 2003) for the full workings out and the assumptions made.* To cut things short, the kriging weights can be found by solving the matrix equation:

{% include equation.html file="images/posts/article-2/Equation_3.png"
alt="equation 3" number="3" height="66" %}

where *&sigma;<sub>ij</sub><sup>2</sup>* is the covariance between known points *z<sub>i</sub>* and 
*z<sub>j</sub>*, and *&sigma;<sub>oi</sub><sup>2</sup>* is the covariance between unknown point *z<sub>o</sub>* and known point *z<sub>i</sub>*. Given the simplifications resulting from the stationarity assumptions *not* discussed above, the covariance between points can be determined using their semivariance as:

$
\sigma^2\left( x_i, x_j \right) = \sigma^2 - \gamma\left( h \right)
$..........(4)

where *&sigma;<sup>2</sup>(x<sub>i</sub>, x<sub>j</sub>)* is the covariance between *x<sub>i</sub>* and *x<sub>j</sub>*, *h* is the lag distance or lag between these 2 points, *&gamma;* is the semivariance, and *&sigma;<sup>2</sup>* is the sample variance.

For simplicity, we can rewrite equation (3) in vector notation as:

$ \Sigma^2 \cdot \Lambda = \Sigma_o^2$..........(5)

Once we have solved Equation (5) for *&Lambda;*, we can estimate the value of *Z* at all points on a *(x, y)* grid of *M* points:

$
\hat{Z} = \Lambda^TZ
$..........(6)

where *&#7824;* is an *M*-element vector of estimated values, *Z* is an *I*-element of known values, and *&Lambda;<sup>T</sup>* is an *I* x *M* matrix of kriging weights. The corresponding Simple Kriging variance (or error in the estimation) is determined by:

$
\Sigma_{SK}^2 = \sigma^2 - \Lambda^T\Sigma_o^2
$..........(7)
