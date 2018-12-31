
Background('white')

static = Circle(center=(0,0), radius=0.5, border_color='grey')
move_center = Circle(center=(0,0), radius=1, hidden=True)

moving = Circle(radius=0.5, center=move_center.value, border_color='grey')
move_head = Circle(radius=0.5,
	center=move_center.value,
	angle=lambda t: angle(t*2),
	hidden=True,
)

penline = Line(p1=move_head.value, p2=moving.center, color='grey')
cardioid = Graph(move_head.value, border_color='red')
