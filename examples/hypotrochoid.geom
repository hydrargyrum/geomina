
Background('white')

reverse = lambda f: lambda t: f(-2*t)

N = 2/3.

base = Circle(radius=1, center=(0, 0), border_color='grey')
motor = Circle(radius=N, center=(0, 0), hidden=True)
moving = Circle(center=motor.value, radius=1-N, angle=reverse(angle), border_color='grey')
radius = Line(p1=moving.center, p2=moving.value, color='grey')
hypotrochoid = Graph(radius.p2, border_color='red')
