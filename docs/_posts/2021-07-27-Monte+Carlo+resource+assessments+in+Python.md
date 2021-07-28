---
layout: post
draft: false
title:  "Monte Carlo resource assessments in Python"
tags: python motecarlo volumetrics
image: empty.png
notebook: 1-MonteCarlo-Resource-Assessments-part1
---
We explore in this article how to easily generate your own Monte Carlo simulations in Python using a resource assessment as an example. The methodologies detailed here can however be adapted to any problem where a Monte Carlo simulation is desired.<!--more-->
There are many advantages to using Python for this: 
- It's totally free — no need for any extensions to Excel (or for Excel for that matter...);
- It's not a black box — you know what is happening under the hood;
- It's fully customizable — you can finally tailor the solution to your problem, including the outputs;
- It is easy to export your results to a wide variety of destinations, including raster and vector images, Excel spreadsheets, or even \\(\LaTeX\\) documents.

Though some familiarity with Python is desirable, advanced knowledge of the language isn't needed and the code provided below should be relatively easy to adapt to your own needs. We will mostly be using [SciPy's](https://www.scipy.org) [*statistical submodule*](https://docs.scipy.org/doc/scipy/reference/stats.html) for calculations, [Pandas](https://pandas.pydata.org) for generating and summarizing results, and a combination of [Matplotlib](https://matplotlib.org)/[seaborn](https://seaborn.pydata.org) for plotting. Using seaborn for plotting automatically handles a lot of the plot formatting.

First, we will see how we can generate random variates from a known distribution. We will then apply this knowledge and generate random variates for all the input parameters for a resource calculation, before calculating the corresponding resource distribution and creating some reporting elements. Finally, we will discuss potential next steps to take things a little further.


## Generating random variates from a distribution with SciPy

Let's generate 10,000 random variates from a normal distribution with a mean of 3 and a standard deviation of 2. For this, we can use SciPy's [*norm*](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html) continuous distribution class to instantiate a normal distribution object with the desired parameters<!--: `distribution = norm(loc=3, scale=2)`-->. We can then use its [*rvs( )*](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_continuous.rvs.html) method to generate \\(n\\) random variates.

### Import necessary libraries


```python
from math import log, exp

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import (norm, lognorm, 
                         gamma, percentileofscore)

import seaborn as sns
```

### Generate random variates and ideal distribution


```python
# instantiate normal distribution object with mean=3, std=2
distribution = norm(loc=3, scale=2)

# generate n random variates using 'rvs' method
n = 10_000
rv = distribution.rvs(int(n))

# generate (x, y) data for the ideal distribution
x = np.linspace(-6.5, 8.5)
probability = distribution.pdf(x)
```

### Plot histogram of results

Seaborn has a very handy function [*histplot*](https://seaborn.pydata.org/generated/seaborn.histplot.html) for plotting histograms we can use:


```python
# create Pyplot axes for plotting results
fig, ax = plt.subplots()

# plot a histogram of the random variates with seaborn
sns.histplot(
    rv,                    # unbinned data to plot
    bins=40,               # number of bins/bars
    stat='density',        # method for normalising bar height
    ax=ax,                 # axes on which to plot the histogram
    label='Sample data'    
)
    
# plot the ideal distribution
ax.plot(x, probability, c='k', ls=':', 
        label='Ideal distribution')
    
# format title and add legend to plot
ax.set_title("$n={:,.0f}$".format(n))
ax.legend(loc='upper left')

plt.show()
```


    
<figure>
    <p>
        <a href="{{ site.url }}assets/images/posts/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_files/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_5_0.png">
        <img src="{{ site.url }}assets/images/posts/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_files/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_5_0.png" alt="png" class="scaled"/>
        </a>
        <figcaption>Random variates from a known distribution.
        &nbsp;(click to enlarge)
        </figcaption>
    </p>
</figure>
    


> We set the `stat` argument to `density` for the histogram to normalize its total area to 1 so it can be compared to our ideal distribution.

### A note on distributions and their parameters in SciPy

In addition to the normal distribution used above, there are many others available in SciPy, all featuring similar functionalities. The average geoscientist should easily find what they need:

- Log-normal ([*lognorm*](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html)) 
- Beta ([*beta*](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html))
- Triangular ([*triang*](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.triang.html))
- Truncated normal ([*truncnorm*](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.truncnorm.html))
- And many more (full list [here](https://docs.scipy.org/doc/scipy/reference/stats.html#continuous-distributions))

The parameters used to define these distributions are not always as user friendly as one might hope, and depending on the distribution some calculations may be needed to get to them. To make things a little simpler going forward, we will therefore create some functions to instantiate SciPy distribution objects using more user friendly parameters, especially for the log-normal distribution which we will also be using. The two functions below do this taking the \\(P_{90}\\) and \\(P_{10}\\) as input parameters; similar functions could be written for other distributions if needed.


```python
# define easy to call normal distribution
def norm_dist(p90, p10):
    if p90 > p10:
        p90, p10 = p10, p90
    mean = (p90 + p10) / 2 
    std = (p10 - p90) / (norm.ppf(0.9) - norm.ppf(0.1))
    return norm(loc=mean, scale=std)
    
# define easy to call log-normal distribution
def lognorm_dist(p90, p10):
    if p90 > p10:
        p90, p10 = p10, p90
    std = log(p10 / p90) / (norm.ppf(0.9) - norm.ppf(0.1))
    mean = (log(p10) - 2**0.5 * std 
            * (gamma.ppf(0.8, a=0.5, scale=1))**0.5)
    return lognorm(s=std, scale=exp(mean))
```

## Generating random variates for volumetric parameters

We can now define distributions for the input parameters of our resource assessment and generate random variates for each parameter. We will store these in a Python `dict` so we can use this dictionary's keys to create corresponding columns in a Pandas DataFrame, and then loop through these keys to populate each column with appropriate random variates.


```python
# define dictionary of volumetric parameters
params = {
    'GRV': lognorm_dist(p90=100e6, p10=250e6),
    'NTG': norm_dist(p90=0.6, p10=0.8),
    'Porosity': norm_dist(p90=0.125, p10=0.225),
    'Sw': norm_dist(p90=0.15, p10=0.45),
    'FVF': norm_dist(p90=1.1, p10=1.3),
    'RF': norm_dist(p90=0.15, p10=0.25),
}

# number of samples in our simulation
num_samples = 100_000

# create an empty DataFrame with a column for each input parameter
realisations = pd.DataFrame([], columns=params)


# loop through key, value pairs from the parameters
# dictionary generating their random variates
# and storing the result in the correct column of
# the DataFrame
seed = 2
for param, dist in params.items():
    realisations[param] = dist.rvs(
        num_samples,
        random_state=seed
    )
    seed = seed*2
```

> Note: defining the `random_state` argument in `rvs` is not a requirement. I have opted to do this here so the outputs are always the same (still 'random', just the same 'random' every time). I have been cautious to change the random state for each parameter to avoid unwanted correlation between parameters.


### Random variates summary

Using Pandas' [*describe( )*](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html?highlight=describe) method and specifying a list of `percentiles`, we can easily generate a table of summary statistics for the input parameters. Along with our chosen percentiles, this will also provide mean, standard deviation, and min &amp; max for each parameter. This is useful to check we have experimental distributions that match our desired ones.


```python
realisations.describe(percentiles=[0.1, 0.5, 0.9])
```




<div>
<style scoped="">
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
<thead>
<tr style="text-align: right;">
<th></th>
<th>GRV</th>
<th>NTG</th>
<th>Porosity</th>
<th>Sw</th>
<th>FVF</th>
<th>RF</th>
</tr>
</thead>
<tbody>
<tr>
<th>count</th>
<td>100,000</td>
<td>100,000</td>
<td>100,000</td>
<td>100,000</td>
<td>100,000</td>
<td>100,000</td>
</tr>
<tr>
<th>mean</th>
<td>1.7e+08</td>
<td>0.700</td>
<td>0.175</td>
<td>0.300</td>
<td>1.200</td>
<td>0.200</td>
</tr>
<tr>
<th>std</th>
<td>6.2e+07</td>
<td>0.0778</td>
<td>0.0390</td>
<td>0.117</td>
<td>0.0782</td>
<td>0.0392</td>
</tr>
<tr>
<th>min</th>
<td>3.8e+07</td>
<td>0.340</td>
<td>-0.00157</td>
<td>-0.189</td>
<td>0.854</td>
<td>0.0366</td>
</tr>
<tr>
<th>10%</th>
<td>1.0e+08</td>
<td>0.600</td>
<td>0.125</td>
<td>0.149</td>
<td>1.100</td>
<td>0.150</td>
</tr>
<tr>
<th>50%</th>
<td>1.6e+08</td>
<td>0.700</td>
<td>0.175</td>
<td>0.300</td>
<td>1.200</td>
<td>0.200</td>
</tr>
<tr>
<th>90%</th>
<td>2.5e+08</td>
<td>0.800</td>
<td>0.225</td>
<td>0.450</td>
<td>1.300</td>
<td>0.250</td>
</tr>
<tr>
<th>max</th>
<td>7.5e+08</td>
<td>1.029</td>
<td>0.331</td>
<td>0.782</td>
<td>1.529</td>
<td>0.364</td>
</tr>
</tbody>
</table>
</div>



Close inspection reveals values for net-to-gross, porosity and \\(S_w\\) that fall outside of desired bounds. We can address this with Pandas' [*clip( )*](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.clip.html) method and clip these outlier values to more reasonable ones.


```python
realisations['Porosity'] = realisations['Porosity'].clip(lower=0.1)
realisations['Sw'] = realisations['Sw'].clip(lower=0.15, upper=0.70)
realisations['NTG'] = realisations['NTG'].clip(upper=1)

realisations.describe(percentiles=[0.1, 0.5, 0.9])
```




<div>
<style scoped="">
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
<thead>
<tr style="text-align: right;">
<th></th>
<th>GRV</th>
<th>NTG</th>
<th>Porosity</th>
<th>Sw</th>
<th>FVF</th>
<th>RF</th>
</tr>
</thead>
<tbody>
<tr>
<th>count</th>
<td>100,000</td>
<td>100,000</td>
<td>100,000</td>
<td>100,000</td>
<td>100,000</td>
<td>100,000</td>
</tr>
<tr>
<th>mean</th>
<td>1.7e+08</td>
<td>0.700</td>
<td>0.175</td>
<td>0.306</td>
<td>1.200</td>
<td>0.200</td>
</tr>
<tr>
<th>std</th>
<td>6.2e+07</td>
<td>0.0778</td>
<td>0.0381</td>
<td>0.107</td>
<td>0.0782</td>
<td>0.0392</td>
</tr>
<tr>
<th>min</th>
<td>3.8e+07</td>
<td>0.340</td>
<td>0.100</td>
<td>0.150</td>
<td>0.854</td>
<td>0.0366</td>
</tr>
<tr>
<th>10%</th>
<td>1.0e+08</td>
<td>0.600</td>
<td>0.125</td>
<td>0.150</td>
<td>1.100</td>
<td>0.150</td>
</tr>
<tr>
<th>50%</th>
<td>1.6e+08</td>
<td>0.700</td>
<td>0.175</td>
<td>0.300</td>
<td>1.200</td>
<td>0.200</td>
</tr>
<tr>
<th>90%</th>
<td>2.5e+08</td>
<td>0.800</td>
<td>0.225</td>
<td>0.450</td>
<td>1.300</td>
<td>0.250</td>
</tr>
<tr>
<th>max</th>
<td>7.5e+08</td>
<td>1.0000</td>
<td>0.331</td>
<td>0.700</td>
<td>1.529</td>
<td>0.364</td>
</tr>
</tbody>
</table>
</div>



## Volumetric calculations and reporting


### Calculating resource distribution

The calculation below assumes that the gross rock volume is in \\(m^3\\) and returns a result in \\(mmbbl\\).


```python
realisations['STOOIP'] = (realisations['GRV']
                     * realisations['NTG']
                     * realisations['Porosity']
                     * (1 - realisations['Sw'])
                     / realisations['FVF']
                     / 1_000 / 159)
realisations['Resource'] = realisations['STOOIP'] * realisations['RF']
```

### Plotting the results

Let's use seaborn again to plot a summary histogram and an empirical cumulative distribution function of the STOOIP distribution:


```python
fig, ax = plt.subplots(nrows=2, figsize=(8.3, 11.7))

# display histogram of distribution in first subplot
sns.histplot(realisations.STOOIP, ax=ax[0], stat='probability', bins=40)

# display empirical cumulative distribution function in second subplot
sns.ecdfplot(realisations.STOOIP, ax=ax[1])

plt.show()
```


    
<figure>
    <p>
        <a href="{{ site.url }}assets/images/posts/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_files/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_17_0.png">
        <img src="{{ site.url }}assets/images/posts/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_files/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_17_0.png" alt="png" class="scaled"/>
        </a>
        <figcaption>
        &nbsp;(click to enlarge)
        </figcaption>
    </p>
</figure>
    


### Summary statistics

And we can reuse the `describe()` method to create a new DataFrame with summary statistics for both our input parameters and STOOIP/resource distributions. We take it one step further this time by transposing the DataFrame so the parameters/results are now rows, and only retaining some of the statistics that we reorder. We can also update the column names to something more useful.


```python
summary = realisations.describe(percentiles=[0.1, 0.5, 0.9])

# transpose summary
summary = summary.T

# select columns in desired order
summary = summary[['min', '10%', '50%', '90%', 'max', 'mean']]

# update column names
summary.columns = ['Min', 'P90', 'P50', 'P10', 'Max', 'Mean']

summary
```




<div>
<style scoped="">
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
<thead>
<tr style="text-align: right;">
<th></th>
<th>Min</th>
<th>P90</th>
<th>P50</th>
<th>P10</th>
<th>Max</th>
<th>Mean</th>
</tr>
</thead>
<tbody>
<tr>
<th>GRV</th>
<td>3.8e+07</td>
<td>1.0e+08</td>
<td>1.6e+08</td>
<td>2.5e+08</td>
<td>7.5e+08</td>
<td>1.7e+08</td>
</tr>
<tr>
<th>NTG</th>
<td>0.340</td>
<td>0.600</td>
<td>0.700</td>
<td>0.800</td>
<td>1.0000</td>
<td>0.700</td>
</tr>
<tr>
<th>Porosity</th>
<td>0.100</td>
<td>0.125</td>
<td>0.175</td>
<td>0.225</td>
<td>0.331</td>
<td>0.175</td>
</tr>
<tr>
<th>Sw</th>
<td>0.150</td>
<td>0.150</td>
<td>0.300</td>
<td>0.450</td>
<td>0.700</td>
<td>0.306</td>
</tr>
<tr>
<th>FVF</th>
<td>0.854</td>
<td>1.100</td>
<td>1.200</td>
<td>1.300</td>
<td>1.529</td>
<td>1.200</td>
</tr>
<tr>
<th>RF</th>
<td>0.0366</td>
<td>0.150</td>
<td>0.200</td>
<td>0.250</td>
<td>0.364</td>
<td>0.200</td>
</tr>
<tr>
<th>STOOIP</th>
<td>7.489</td>
<td>36.92</td>
<td>67.97</td>
<td>123.3</td>
<td>486.9</td>
<td>75.46</td>
</tr>
<tr>
<th>Resource</th>
<td>1.108</td>
<td>6.826</td>
<td>13.34</td>
<td>25.50</td>
<td>100.8</td>
<td>15.09</td>
</tr>
</tbody>
</table>
</div>



### Export results

Matplotlib provides the option to save a figure as a file, with multiple file formats available, including PDF, SVG, PNG and JPEG. Likewise, Pandas allows direct exports to a number of formats, including CSV and Excel *.xlsx* spreadsheets.


```python
# export STOOIP historgram to a PDF file
fig.savefig('./STOOIP.pdf')

# export summary statistcs to an Excel spreadsheet
summary.to_excel('./summary.xlsx')
```

## Summary

We have seen in this article how to generate random variates from a known distribution and applied this to generate random variates for the input parameters of our resource calculation.
using Pandas for STOOIP/resource calculations and exporting tables to Excel
using Matplotlib/seaborn to plot results and export.



## Where next?

- [ ] correlated variables
- [ ] area depth from grid
- [ ] GRV from 2 grids
- [ ] risked distributions
- [ ] multiple prospects / consolidation

### Different workflows

- area-depth
- 1/2 grids

### More advanced sampling

The `rvs` method is already adding a layer of abstraction in that it is handling all the sampling effort. Under the hood, it is generating \\(n\\) pseudo-random numbers from a uniform distribution over \\( \left[0,1\right]\\) and using the inverse of an appropriate cumulative distribution function to convert these to random variates of the desired distribution. With increasing numbers of parameters, this could lead to undersampling of parts of the sample space. One solution to address this is by using brute force and increasing the number of samples.

(sensitivity figure/discussion here - 100,000 samples/200 realisations).


<figure>
<p>
<a href="{{ site.url }}assets/images/posts/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_files/1-sensitivity.png">
<img alt="png" class="scaled" src="{{ site.url }}assets/images/posts/2021-07-27-Monte%2BCarlo%2Bresource%2Bassessments%2Bin%2BPython_files/1-sensitivity.png"/>
</a>
<figcaption>Figure title.</figcaption>
</p>
</figure>

    
Another solution is to ditch `rvs` and take control of sampling. In this case we need to generate our own samples over \\( \left[0,1\right]\\) and transform them to random variates with the `ppf` method which provides an inverse cumulative probability function for a distribution. There are two main advantages to doing this:

1. You can opt for more advanced sampling techniques like Latin hypercubes, orthogonal sampling, or low-discrepancy sequences; this is no longer pseudo-random though and enters the realm of Quasi Monte Carlo simulation. Given the low number of dimensions typical of resource calculations it is likely to offer only limited advantages. If you are using Scipy version 1.7 or later, it features a [*Quasi Monte Carlo*](https://docs.scipy.org/doc/scipy/reference/stats.qmc.html) module that provides algorithms for Latin hypercubes and low-discrepancy sequences as well as some functionalities handling covariances between dimensions.

2. 


### Portfolio consolidations

pseudo-randomness, sampling, LHC etc. SciPY QMC...

