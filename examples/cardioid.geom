
Background('white')

bigc = Circle(center=(0,0), radius=0.5, border_color='grey')
bigc2 = Circle(center=(0,0), radius=1, hidden=True)
movingc = Circle(radius=0.5, center=bigc2.value, border_color='grey')
movingc2 = Circle(radius=0.5, center=bigc2.value, angle=lambda t: angle(t*2), hidden=True, border_color='grey')

#pendot = Dot(center=movingc2.value)
penline = Line(p1=movingc2.value, p2=movingc.center, color='grey')
cardioid = Graph(movingc2.value, border_color='red')
