---
layout: post
title:  "How to draw rocks in python"
tags: python matplotlib lithologies hatch
image: limestone-crop.jpg
notebook: 1-limestone-hatch
---

Matplotlib offers tantalizing hatching options that will sadly leave most geologists a little frustrated. It's a little like pattern fills in Excel - so much potential until you actually try and use it to make satisfying lithology logs. 

You need not despair however, as Matplotlib's hatch functions can be customized to your heart's content. I show an example here of how to create a standard limestone hatch, but the methodology can be generalized to created pretty much any lithology pattern you want.

<!--more-->

<img src="{{ site.url }}assets/images/posts/article-1/hatches.png" alt="existing hatches" width="500px" />

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.hatch import HatchPatternBase, _hatch_types
import matplotlib.patches as patches
from matplotlib import rcParams


path_vertices = np.array([[0.25,0.25],  # MOVETO
                          [0.25,0.75],  # LINETO
            
                          [0,0.25],     # MOVETO
                          [1,0.25],     # LINETO
                             
                          [0,0.75],     # MOVETO
                          [1,0.75],     # LINETO
                             
                          [0.75,0.75],  # MOVETO
                          [0.75,1],     # LINETO
                             
                          [0.75,0.],    # MOVETO
                          [0.75,0.25]]) # LINETO


# reduce linewidth of hatch patterns
rcParams['hatch.linewidth'] = 0.25

class LimestoneHatch(HatchPatternBase):
    
    def __init__(self, hatch, density):

        # number of times the path will be repeated in one direction
        # within the unit square
        self.num_lines = int((hatch.count('l') + \
                            hatch.count('L')) * density)   
        
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



_hatch_types.append(LimestoneHatch)
```



<figure>
    <p>
        <img class="scaled" src="{{ site.url }}assets/images/posts/article-1/custom_hatches.png" alt="custom hatches"/>
        <figcaption><b>Figure 2:</b> Customized limestone hatch in action.</figcaption>
    </p>
</figure>


<img src="{{ site.url }}assets/images/posts/article-1/hatch_dictionary.png" alt="hatch dictionary" width="550px" />

{% include image.html file="assets/images/posts/article-1/hatch_dictionary.png"
alt="custom hatches" number="3"
caption="This is the Jekyll logo." %}