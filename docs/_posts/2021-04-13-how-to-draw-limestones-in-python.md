---
layout: post
title:  "How to draw rocks in Python"
tags: python matplotlib lithologies hatch
image: limestone-crop.jpg
notebook: 1-limestone-hatch
---

Matplotlib offers tantalizing [hatching](https://matplotlib.org/stable/gallery/shapes_and_collections/hatch_demo.html) options that will sadly leave most geologists asking for more. It's a bit like pattern fills in Excel - so much potential until you actually try and use it to make satisfying lithology logs. 

Unlike Excel however, you can customize Matplotlib's hatch function to your heart's content. I show an example here of how to create a standard limestone pattern, but the methodology can be generalized to created pretty much any lithology pattern you want.

<!--more-->

## Built-in pattern options

Figure 1 shows some of the lithology patterns you can create using Matplotlib's built-in hatch types. Convincing patterns can be made for basic clastic lithologies, but there is no way to make an adequate pattern for carbonates (or indeed other more advanced lithology options). See [here](https://matplotlib.org/stable/gallery/shapes_and_collections/hatch_style_reference.html) for a reference of the built-in hatch styles.

{% include image.html file="posts/article-1/hatches.png"
alt="custom hatches" number="1"
caption="Some lithology patterns using Matplotlib's built-in hatches." %}

## Customized limestone pattern

Below is some code that implements a customized limestone hatch pattern. A hatch pattern is nothing more than a [Path](https://matplotlib.org/stable/api/path_api.html#matplotlib.path.Path) object. It must however fit within a unit square and will be repeated in the `x` and `y` directions to fill the entire hatched area. Care should therefore be taken to ensure the sides of the pattern match up as needed. 

The `path_vertices` array contains the coordinates of the vertices that make up the path of our desired pattern. This path will ultimately be used by Matplotlib to create a Path object that it will use as the hatch pattern. A Path object requires an array of vertices and an array of codes, the codes telling the renderer what to do with the "pen" between vertices. In our example, the path is made up of 5 segments, with the pen moving at the start of each segment. 

The `LimestoneHatch` class automatically handles the codes for our path (as well as for an arbitrary number or segments). It also handles the identification of the flag "L" we will need to use our custom limestone hatch along with any repetitions of the path within the unit square needed for higher hatch densities. The associated Jupyter notebook (links to the left in the navigation pane) goes in to more detail on how the `LimestoneHatch` class works.

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

Below is a short script that was used to create Figure 1 with the addition of the custom limestone hatch pattern. All that is needed is to provided the value `L` to the `hatch` argument; the built-in hatch patterns continue to work as expected. If you have saved the above code into a separate Python script, you will need to import it here; doing so will automatically add the `LimestoneHatch` hatch. The output is shown in Figure 2.

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
           'L',
           'LL']
labels = ['Conglomerate ' + u'\u2713',
          'Sandstone ' + u'\u2713',
          'Shale ' + u'\u2713',
          'Shaly sandstone ' + u'\u2713',
          'Limestone ' + u'\u2713',
          'Limestone ' + u'\u2713']
colors = ['orange',
          'yellow',
          'peru',
          'yellow',
          'lightblue',
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
ax.set_xlim(-.5, 12)
ax.set_ylim(0.9, -.25)
ax.set_xticks([])
ax.set_yticks([])
ax.axis("off")

plt.show()
```


{% include image.html file="posts/article-1/custom_hatches.png"
alt="custom hatches" number="2"
caption="Customized limestone hatch in action." %}

In fact, our custom limestone hatch is now ready to be used with any Matplotlib object that accepts `hatch` as an argument: most polygons including `bar`, `fill_between`, `fill_betweenx`, `contourf`, and children of `Polygon`. This means it can be used in a wide variety of charts made with Matplotlib like lithology logs, wire-line & petrophyscial logs, chronostratigraphic charts, maps, _etc._

## Where next?

The next step is to create a custom dictionary of patterns to account for a wider variety of lithological options. Ultimately, any path can be used to create a hatch pattern, though the class that creates the required path vertice and code arrays needs to be updated accordingly.

Figure 3 shows some examples of the variety of patterns that can be created. Though a little more complex than the limestone example above, they all follow the same methodology of repeating a base pattern (defined by its `vertices` and `codes` arrays) over a unit square. Care must however be taken when choosing a flag for each pattern as you don't to be calling additional patterns by mistake. Had we used "limestone" as the flag for our example, circles would have appeared every time we used it: "o" is indeed a flag for the small circle hatch!

{% include image.html file="posts/article-1/hatch_dictionary.png"
alt="hatches dictionary" number="3"
caption="Example dictionary of multiple customized hatches." %}

I hope you have found this article helpful and that it will encourage you to customize Matplotlib (or other Python libraries) to better suit your needs. In future articles we will explore other elements of geological drawing.