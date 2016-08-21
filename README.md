# What is geomina? #

Geomina is a program to plot *GEOM*etric *ANIM*ations, for example cardioids or Bézier splines.
Geomina takes a simple text input file describing the animation scene and renders it to frame images or to GIF.

The scene description consists in a declaration of shapes to render and how their coordinates should evolve over time.

## Example ##

The following image was rendered with Geomina:

![cardioid](examples/cardioid.gif)

... with the following scene description:

	Background('white')

	static = Circle(center=(0,0), radius=0.5, border_color='grey')
	move_center = Circle(center=(0,0), radius=1, hidden=True)

	moving = Circle(radius=0.5, center=move_center.value, border_color='grey')
	move_head = Circle(radius=0.5, center=move_center.value, angle=lambda t: angle(t*2), hidden=True, border_color='grey')

	penline = Line(p1=move_head.value, p2=moving.center, color='grey')
	cardioid = Graph(move_head.value, border_color='red')

## Dependencies ##

Geomina depends on PyCairo for the rendering part and may require ImageMagick for saving animations to GIF.

## License ##

Geomina is licensed under the [Do What the Fuck You Want to Public License](http://wtfpl.net)
