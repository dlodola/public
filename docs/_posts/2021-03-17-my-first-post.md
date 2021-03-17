---
layout: post
title:  "First Post"
tags: python matplotlib lithologies
---


```python
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
