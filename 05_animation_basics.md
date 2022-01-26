# Animations with Matplotlib

This notebook shows how to use the `FuncAnimation` function from the `matplotlib.animation` module to create animated plots. 


```python
import os

%matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
```

Let's understand the basics of matplotlib animation with a simple example. We will define 3 positions and we will create an animation of a point moving between them.


```python
points = [(0.1, 0.5), (0.5, 0.5), (0.9, 0.5)]
```

Then we use the `FuncAnimation` class which makes an animation by repeatedly calling a function and saving the output as a frame in the animation.

We need to define a function that takes the frame number and generates a plot from it. Here we define a function `animation` that takes the frame index and creates a plot from the point at the same index in the `points` list. So at frame 0, it will display the first point, frame 1 the second point and so on.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
fig.tight_layout(rect=[0, 0.03, 1, 0.95])

def animate(i):
    ax.clear()
    # Get the point from the points list at index i
    point = points[i]
    # Plot that point using the x and y coordinates
    ax.plot(point[0], point[1], color='green', 
            label='original', marker='o')
    # Set the x and y axis to display a fixed range
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
ani = FuncAnimation(fig, animate, frames=len(points),
                    interval=500, repeat=True)
plt.close()
```

The animation is now contained in the `ani` object. We can call `save()` and save the result as an animated GIF. We need to specify a `writer` that supports the output format.


```python
output_folder = 'output'
output_path = os.path.join(output_folder, 'simple_animation.gif')
ani.save(output_path, dpi=300,
         writer=PillowWriter(fps=1))
```

We can also use the `to_jshtml()` function to create an HTML representation of the animation and display in a Jupyter notebook.


```python
from IPython.display import HTML
#HTML(ani.to_jshtml())
```


```python

```
