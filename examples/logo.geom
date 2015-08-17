Background('w')

Line((-5/8, 0), lambda t: (-5/8-t/8, 0), color='k')
Circle(center=(-3/4, 0), radius=1/8, full=False, angle=lambda t: angle(t*6/7), border_color='k')

Line((-5/8, 0), lambda t: (-5/8+t/4, 0), color='k')
Circle(center=(-1/2, 0), radius=1/8, full=False, angle=lambda t: angle(t*6/7+1/7), border_color='k')

Circle(center=(-1/4, 0), radius=1/8, full=False, border_color='k')

m1 = Circle(center=(0, 0), radius=1/8, full=False, angle=lambda t: angle(t/4+3/8), border_color='k')
m2 = Circle(center=(0, 0), radius=1/8, full=False, sweep_start=angle(1/8), sweep_end=lambda t: angle(-t/4+1/8), border_color='k')
Line(p1=m1.center, p2=m1.value, color='k')
Line(p1=m2.center, p2=m2.sweep_end_value, color='k')

Line(p1=lambda t: (1/4, -t/8), p2=lambda t: (1/4, t/8), color='k')
Circle(center=(1/4, 0), radius=1/8, full=False, sweep_start=lambda t: angle(-t/8 + 1/4), sweep_end=lambda t: angle(t/8 + 1/4), border_color='k')
Circle(center=(1/4, 0), radius=1/8, full=False, sweep_start=lambda t: angle(-t/8 - 1/4), sweep_end=lambda t: angle(t/8 - 1/4), border_color='k')

n1 = Circle(center=(1/2, 0), radius=lambda t: t/8, full=False, sweep_start=angle(3/8), sweep_end=lambda t: angle(t/4+3/8), border_color='k')
n2 = Circle(center=(1/2, 0), radius=lambda t: t/8, full=False, sweep_start=angle(-1/8), sweep_end=lambda t: angle(t/4-1/8), border_color='k')
Line(p1=n1.sweep_end_value, p2=n2.sweep_end_value, color='k')

Circle(center=(3/4, 0), radius=1/8, full=False, sweep_start=lambda t: angle(3/4 - 3*t/8), sweep_end=lambda t: angle(3/4 + 3*t/8), border_color='r')
Line(p1=lambda t: (3/4 - t/8, 0), p2=lambda t: (3/4 + t/8, 0), color='r')
