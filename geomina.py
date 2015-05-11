#!/usr/bin/env python

import numpy
from numpy import linspace
import matplotlib.pyplot as plt
import matplotlib.animation
import matplotlib.colors
import matplotlib.cm
from math import cos, sin, tan, pi, e, fmod
import sys
import os
from argparse import ArgumentParser


__all__ = ('''cos sin tan pi e fmod
	Plotter Circle Dot Line Graph Drawable FillableDrawable Label
	angle shift eval_at formatter
	global_registry'''.split())


global_registry = []


def angle(t, start_angle=0):
	return (t * 2 * pi + start_angle) % (2 * pi)

def shift(t, move):
	return (t + move) % 1

def eval_at(f, t):
	if callable(f):
		return f(t)
	else:
		return f

def formatter(s):
	return s.__mod__


class Plotter:
	def __init__(self):
		self.fig = plt.figure()#facecolor='#000000')
		self.anim = None

		plt.axis('off')
		plt.axis('equal')

	def set_resolution(self, x, y):
		dpi = 100.
		self.fig.set_dpi(dpi)
		self.fig.set_size_inches(x / dpi, y / dpi)

	def set_window(self, minx, miny, maxx, maxy):
		plt.xlim(minx, maxx)
		plt.ylim(miny, maxy)

	# TODO setup axes, etc
	def _plot(self, objs, t_start, t_end):
		def draw(t):
			for obj, plot in zip(objs, plots):
				obj.draw(t, plot)
			return plots

		objs = [obj for obj in objs if obj.visible]
		plots = [obj.create() for obj in objs]

		t_values = linspace(t_start, t_end)

		self.anim = matplotlib.animation.FuncAnimation(self.fig, draw, frames=t_values, blit=True)

	def show(self, objs, t_start=0, t_end=1):
		self._plot(objs, t_start, t_end)
		plt.show()

	def save(self, objs, file, t_start=0, t_end=1):
		self._plot(objs, t_start, t_end)
		self.anim.save(file, 'imagemagick')


class Drawable(object):
	def __init__(self, fill_color='none', border_color=None, border_width=None, alpha=1, hidden=False, register=True):
		self.fill_color = fill_color or 'none'
		self.border_color = border_color or 'black'
		self.border_width = border_width
		self.alpha = alpha

		self.visible = not hidden
		if register:
			global_registry.append(self)


class FillableDrawable(Drawable):
	def create(self):
		plot, = plt.fill([0], [0], facecolor=self.fill_color, edgecolor=self.border_color, linewidth=self.border_width)
		plot.set_alpha(self.alpha)
		return plot


class Circle(FillableDrawable):
	def __init__(self, center, radius, full=True, angle=angle, **kw):
		super(Circle, self).__init__(**kw)

		self._center = center
		self._radius = radius
		self._angle = angle
		self.full = full

	def center(self, t):
		return eval_at(self._center, t)

	def radius(self, t):
		return eval_at(self._radius, t)

	def angle(self, t):
		return eval_at(self._angle, t)

	def draw(self, t_end, plot):
		c = self.center(t_end)
		r = self.radius(t_end)
		
		if self.full:
			max = 1
		else:
			max = t_end

		plot.set_xy(numpy.array([[cos(self.angle(t)) * r + c[0] for t in linspace(0, max)],
		                         [sin(self.angle(t)) * r + c[1] for t in linspace(0, max)]]).T)

	def value(self, t):
		c = self.center(t)
		r = self.radius(t)
		return (cos(self.angle(t)) * r + c[0], sin(self.angle(t)) * r + c[1])


class Dot(Circle):
	def __init__(self, center, color=None, fill=True):
		color = color or 'black'
		fill_color = fill and color or 'none'
		super(Dot, self).__init__(center=center, radius=0.05, fill_color=fill_color, border_color=color)


class Line(Drawable):
	def __init__(self, p1, p2, color=None, **kw):
		super(Line, self).__init__(border_color=color, **kw)

		self._p1 = p1
		self._p2 = p2

	def p1(self, t):
		return eval_at(self._p1, t)

	def p2(self, t):
		return eval_at(self._p2, t)

	def value(self, t):
		p1 = self.p1(t)
		p2 = self.p2(t)
		return ((1 - t) * p1[0] + t * p2[0]), ((1 - t) * p1[1] + t * p2[1])
	
	def create(self):
		k = {}
		if self.border_width is not None:
			k['linewidth'] = self.border_width
		plot, = plt.plot([], [], color=self.border_color, **k)
		plot.set_alpha(self.alpha)
		return plot

	def draw(self, t_end, plot):
		p1 = self.p1(t_end)
		#v = self.value(t_end)
		p2 = self.p2(t_end)
		plot.set_data([p1[0], p2[0]], [p1[1], p2[1]])


class Graph(FillableDrawable):
	def __init__(self, f, **kw):
		super(Graph, self).__init__(**kw)
		self._f = f
	
	def value(self, t):
		return self._f(t)

	def draw(self, t_end, plot):
		# TODO be smarter for the number of points and placement/density of points
		points = numpy.array(list(self.points(linspace(0, t_end, max(1, t_end * 200)))))
		plot.set_closed(False)
		plot.set_xy(points)

	def points(self, t_values):
		for t in t_values:
			yield self._f(t)


class Label(Drawable):
	def __init__(self, text, pos, **kw):
		super(Label, self).__init__(**kw)
		self._text = text
		self._pos = pos
	
	def create(self):
		plot = plt.text(0, 0, '', color=self.fill_color)
		return plot
	
	def draw(self, t, plot):
		pos = eval_at(self._pos, t)
		plot.set_position(pos)
		plot.set_text(eval_at(self._text, t))


class Annotation(Drawable):
	def __init__(self, text, pos, **kw):
		super(Annotation, self).__init__(**kw)
		self._text = text
		self._pos = pos
	
	def create(self):
		plot = plt.annotate('', (0, 0), xycoords='data', color=self.fill_color, arrowprops=dict(arrowstyle="->"))
		return plot
	
	def draw(self, t, plot):
		pos = eval_at(self._pos, t)
		plot.xy = pos
		plot.xytext = plot.xy
		plot.set_text(eval_at(self._text, t))


def run_file(opts):
	plotter = Plotter()
	plotter.set_window(*opts.zone)
	plotter.set_resolution(*opts.size)
	
	g = globals()
	vars = dict((k, g[k]) for k in __all__)
	vars['plotter'] = plotter
	module = execfile(opts.geomfile, vars, vars)

	if opts.output:
		plotter.save(global_registry, opts.output)
	else:
		plotter.show(global_registry)


def main():
	argparser = ArgumentParser()
	argparser.add_argument('geomfile', metavar='FILE')
	argparser.add_argument('--zone', metavar='X,Y,X,Y', help='virtual canvas zone shown by the output image (default: -2,-2,2,2)', default='-2,-2,2,2')
	argparser.add_argument('--size', metavar='WxH', help='size of output image (width and height, default: 512x512)', default='512x512')
	argparser.add_argument('-o', '--output', metavar='FILE', dest='output')
	opts = argparser.parse_args()

#	if not opts.output:
#		opts.output = os.path.splitext(opts.geomfile)[0] + '.gif'

	zone = opts.zone.split(',')
	if len(zone) != 4:
		argparser.error('zone argument should be if X,Y,X,Y format')
	try:
		zone = map(float, zone)
	except ValueError:
		argparser.error('zone argument should be if X,Y,X,Y format')
	opts.zone = zone

	size = opts.size.split('x')
	if len(size) != 2:
		argparser.error('size argument should be if WxH format')
	try:
		size = map(int, size)
	except ValueError:
		argparser.error('size argument should be if WxH format')
	opts.size = size

	run_file(opts)

if __name__ == '__main__':
	main()

