## Animations with Matplotlib

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
HTML(ani.to_jshtml())
```





<link rel="stylesheet"
href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css">
<script language="javascript">
  function isInternetExplorer() {
    ua = navigator.userAgent;
    /* MSIE used to detect old browsers and Trident used to newer ones*/
    return ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;
  }

  /* Define the Animation class */
  function Animation(frames, img_id, slider_id, interval, loop_select_id){
    this.img_id = img_id;
    this.slider_id = slider_id;
    this.loop_select_id = loop_select_id;
    this.interval = interval;
    this.current_frame = 0;
    this.direction = 0;
    this.timer = null;
    this.frames = new Array(frames.length);

    for (var i=0; i<frames.length; i++)
    {
     this.frames[i] = new Image();
     this.frames[i].src = frames[i];
    }
    var slider = document.getElementById(this.slider_id);
    slider.max = this.frames.length - 1;
    if (isInternetExplorer()) {
        // switch from oninput to onchange because IE <= 11 does not conform
        // with W3C specification. It ignores oninput and onchange behaves
        // like oninput. In contrast, Microsoft Edge behaves correctly.
        slider.setAttribute('onchange', slider.getAttribute('oninput'));
        slider.setAttribute('oninput', null);
    }
    this.set_frame(this.current_frame);
  }

  Animation.prototype.get_loop_state = function(){
    var button_group = document[this.loop_select_id].state;
    for (var i = 0; i < button_group.length; i++) {
        var button = button_group[i];
        if (button.checked) {
            return button.value;
        }
    }
    return undefined;
  }

  Animation.prototype.set_frame = function(frame){
    this.current_frame = frame;
    document.getElementById(this.img_id).src =
            this.frames[this.current_frame].src;
    document.getElementById(this.slider_id).value = this.current_frame;
  }

  Animation.prototype.next_frame = function()
  {
    this.set_frame(Math.min(this.frames.length - 1, this.current_frame + 1));
  }

  Animation.prototype.previous_frame = function()
  {
    this.set_frame(Math.max(0, this.current_frame - 1));
  }

  Animation.prototype.first_frame = function()
  {
    this.set_frame(0);
  }

  Animation.prototype.last_frame = function()
  {
    this.set_frame(this.frames.length - 1);
  }

  Animation.prototype.slower = function()
  {
    this.interval /= 0.7;
    if(this.direction > 0){this.play_animation();}
    else if(this.direction < 0){this.reverse_animation();}
  }

  Animation.prototype.faster = function()
  {
    this.interval *= 0.7;
    if(this.direction > 0){this.play_animation();}
    else if(this.direction < 0){this.reverse_animation();}
  }

  Animation.prototype.anim_step_forward = function()
  {
    this.current_frame += 1;
    if(this.current_frame < this.frames.length){
      this.set_frame(this.current_frame);
    }else{
      var loop_state = this.get_loop_state();
      if(loop_state == "loop"){
        this.first_frame();
      }else if(loop_state == "reflect"){
        this.last_frame();
        this.reverse_animation();
      }else{
        this.pause_animation();
        this.last_frame();
      }
    }
  }

  Animation.prototype.anim_step_reverse = function()
  {
    this.current_frame -= 1;
    if(this.current_frame >= 0){
      this.set_frame(this.current_frame);
    }else{
      var loop_state = this.get_loop_state();
      if(loop_state == "loop"){
        this.last_frame();
      }else if(loop_state == "reflect"){
        this.first_frame();
        this.play_animation();
      }else{
        this.pause_animation();
        this.first_frame();
      }
    }
  }

  Animation.prototype.pause_animation = function()
  {
    this.direction = 0;
    if (this.timer){
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  Animation.prototype.play_animation = function()
  {
    this.pause_animation();
    this.direction = 1;
    var t = this;
    if (!this.timer) this.timer = setInterval(function() {
        t.anim_step_forward();
    }, this.interval);
  }

  Animation.prototype.reverse_animation = function()
  {
    this.pause_animation();
    this.direction = -1;
    var t = this;
    if (!this.timer) this.timer = setInterval(function() {
        t.anim_step_reverse();
    }, this.interval);
  }
</script>

<style>
.animation {
    display: inline-block;
    text-align: center;
}
input[type=range].anim-slider {
    width: 374px;
    margin-left: auto;
    margin-right: auto;
}
.anim-buttons {
    margin: 8px 0px;
}
.anim-buttons button {
    padding: 0;
    width: 36px;
}
.anim-state label {
    margin-right: 8px;
}
.anim-state input {
    margin: 0;
    vertical-align: middle;
}
</style>

<div class="animation">
  <img id="_anim_img71e44e36eca3436daaddb33193277b3c">
  <div class="anim-controls">
    <input id="_anim_slider71e44e36eca3436daaddb33193277b3c" type="range" class="anim-slider"
           name="points" min="0" max="1" step="1" value="0"
           oninput="anim71e44e36eca3436daaddb33193277b3c.set_frame(parseInt(this.value));">
    <div class="anim-buttons">
      <button title="Decrease speed" aria-label="Decrease speed" onclick="anim71e44e36eca3436daaddb33193277b3c.slower()">
          <i class="fa fa-minus"></i></button>
      <button title="First frame" aria-label="First frame" onclick="anim71e44e36eca3436daaddb33193277b3c.first_frame()">
        <i class="fa fa-fast-backward"></i></button>
      <button title="Previous frame" aria-label="Previous frame" onclick="anim71e44e36eca3436daaddb33193277b3c.previous_frame()">
          <i class="fa fa-step-backward"></i></button>
      <button title="Play backwards" aria-label="Play backwards" onclick="anim71e44e36eca3436daaddb33193277b3c.reverse_animation()">
          <i class="fa fa-play fa-flip-horizontal"></i></button>
      <button title="Pause" aria-label="Pause" onclick="anim71e44e36eca3436daaddb33193277b3c.pause_animation()">
          <i class="fa fa-pause"></i></button>
      <button title="Play" aria-label="Play" onclick="anim71e44e36eca3436daaddb33193277b3c.play_animation()">
          <i class="fa fa-play"></i></button>
      <button title="Next frame" aria-label="Next frame" onclick="anim71e44e36eca3436daaddb33193277b3c.next_frame()">
          <i class="fa fa-step-forward"></i></button>
      <button title="Last frame" aria-label="Last frame" onclick="anim71e44e36eca3436daaddb33193277b3c.last_frame()">
          <i class="fa fa-fast-forward"></i></button>
      <button title="Increase speed" aria-label="Increase speed" onclick="anim71e44e36eca3436daaddb33193277b3c.faster()">
          <i class="fa fa-plus"></i></button>
    </div>
    <form title="Repetition mode" aria-label="Repetition mode" action="#n" name="_anim_loop_select71e44e36eca3436daaddb33193277b3c"
          class="anim-state">
      <input type="radio" name="state" value="once" id="_anim_radio1_71e44e36eca3436daaddb33193277b3c"
             >
      <label for="_anim_radio1_71e44e36eca3436daaddb33193277b3c">Once</label>
      <input type="radio" name="state" value="loop" id="_anim_radio2_71e44e36eca3436daaddb33193277b3c"
             checked>
      <label for="_anim_radio2_71e44e36eca3436daaddb33193277b3c">Loop</label>
      <input type="radio" name="state" value="reflect" id="_anim_radio3_71e44e36eca3436daaddb33193277b3c"
             >
      <label for="_anim_radio3_71e44e36eca3436daaddb33193277b3c">Reflect</label>
    </form>
  </div>
</div>


<script language="javascript">
  /* Instantiate the Animation class. */
  /* The IDs given should match those used in the template above. */
  (function() {
    var img_id = "_anim_img71e44e36eca3436daaddb33193277b3c";
    var slider_id = "_anim_slider71e44e36eca3436daaddb33193277b3c";
    var loop_select_id = "_anim_loop_select71e44e36eca3436daaddb33193277b3c";
    var frames = new Array(3);

  frames[0] = "data:image/png;base64,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\
"
  frames[1] = "data:image/png;base64,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\
"
  frames[2] = "data:image/png;base64,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\
"


    /* set a timeout to make sure all the above elements are created before
       the object is initialized. */
    setTimeout(function() {
        anim71e44e36eca3436daaddb33193277b3c = new Animation(frames, img_id, slider_id, 500.0,
                                 loop_select_id);
    }, 0);
  })()
</script>



