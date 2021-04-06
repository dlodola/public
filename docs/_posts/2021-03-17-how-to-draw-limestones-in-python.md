---
layout: post
title:  "How to draw rocks in python"
tags: python matplotlib lithologies hatch
image: limestone-crop.jpg
notebook: 1-limestone-hatch
---

Matplotlib offers tantalizing hatching options that will sadly leave most geologists a little frustrated. It's a little like pattern fills in Excel - so much potential until you actually try and use it to make satisfying lithology logs. 

Unlike Excel however, you can customize Matplotlib's hatch function to your heart's content. I show an example here of how to create a standard limestone hatch, but the methodology can be generalized to created pretty much any lithology pattern you want.

<!--more-->

## Built-in pattern options

Figure 1 shows some of the lithology patterns you can create using Matplotlib's built-in hatch types. Convincing patterns can be made for basic clastic lithologies, but there is no way to make an adequate pattern for carbonates (or indeed more advanced lithology options).

{% include image.html file="posts/article-1/hatches.png"
alt="custom hatches" number="1"
caption="Some lithology patterns using Matplotlib's built-in hatches." %}

## Customized limestone pattern

```python
import numpy as np
from matplotlib.path import Path
from matplotlib.hatch import HatchPatternBase, _hatch_types


path_vertices = np.array([[0.25,0.25],
                          [0.25,0.75],
            
                          [0,0.25],
                          [1,0.25],
                             
                          [0,0.75],
                          [1,0.75],
                             
                          [0.75,0.75],
                          [0.75,1],
                             
                          [0.75,0.],
                          [0.75,0.25]])


class LimestoneHatch(HatchPatternBase):
    
    def __init__(self, hatch, density):

        # number of times the path will be repeated in one direction
        # within the unit square
        self.num_lines = int((hatch.count('L')) * density)   
        
        # total number of vertices for the path once it has been
        # repeated the appropriate number of times within the unit square
        self.num_vertices = (self.num_lines ** 2 * len(path_vertices))


    def set_vertices_and_codes(self, vertices, codes):
        
        steps = np.linspace(0, 1, self.num_lines, endpoint=False)
        offsets = np.array(np.meshgrid(steps,steps)).transpose([1,2,0]) \
                        .reshape((self.num_lines**2, 2)) \
                        .repeat(len(path_vertices), axis=0)
        
        # update values in slice of vertices array
        vertices[:] = np.tile(path_vertices / self.num_lines, 
                              (self.num_lines**2, 1)) + offsets
        
        # update values in slice of codes array
        # all even rows are set to MOVETO & all odd rows to LINETO
        codes[0::2] = Path.MOVETO
        codes[1::2] = Path.LINETO


# add our custom hatch to Matplotlib's list of hatch types
_hatch_types.append(LimestoneHatch)
```

## Using the custom pattern

Below is a short script that was used to create Figure 1 with the custom limestone hatch pattern used as appropriate. All that is needed is to provided the value `L` to the `hatch` argument; the built-in hatch patterns continue to work as expected. If you have saved the above code into a separate Python script, you will need to import it here; doing so will automatically add the `Limestone` hatch. The output is shown in Figure 2.

```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import rcParams


# reduce linewidth of hatch patterns
rcParams['hatch.linewidth'] = 0.25

hatches = ['oo', 
           '...',
           '---',
           '...---',
           'L']
labels = ['Conglomerate ' + u'\u2713',
          'Sandstone ' + u'\u2713',
          'Shale ' + u'\u2713',
          'Shaly sandstone ' + u'\u2713',
          'Limestone ' + u'\u2713']
colors = ['orange',
          'yellow',
          'peru',
          'yellow',
          'lightblue']

fig, ax = plt.subplots(figsize=(8.3,2))
vertices = np.array(([0,1.5,1.5,0,0], [0,0,0.5,0.5,0]))

for i in range(len(hatches)):
    ax.fill_between(vertices[0] + i*2, 
                    vertices[1], 
                    hatch=hatches[i], 
                    fc=colors[i],
                    ec='k',
                    label=labels[i])
    ax.annotate(labels[i], (i*2, .7), size=7.5)
ax.set_xlim(-.5, 10)
ax.set_ylim(0.9, -.25)
ax.set_xticks([])
ax.set_yticks([])
ax.axis("off")

plt.show()
```


{% include image.html file="posts/article-1/custom_hatches.png"
alt="custom hatches" number="2"
caption="Customized limestone hatch in action." %}

In fact, our custom limestone hatch is now ready to be used with Matplotlib object that accepts `hatch` as an argument: most polygons including `bar`, `fill_between`, `fill_betweenx`, `contourf`, and children of `Polygon`. This means it can be used in a wide variety of charts made with Matplotlib like lithology logs, wire-line & petrophyscial logs, chronostratigraphic charts, maps, _etc._

## Where next?

{% include image.html file="posts/article-1/hatch_dictionary.png"
alt="hatches dictionary" number="3"
caption="Example dictionary of multiple customized hatches." %}