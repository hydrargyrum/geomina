#!/usr/bin/env python

from __future__ import division
from math import cos, sin, tan, pi, e, fmod, ceil, floor
import sys
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import tempfile
import subprocess
import shutil
import cairo


__all__ = ('''cos sin tan pi e fmod ceil floor mirror
	Plotter Circle Dot Line Graph Drawable Label Background
	angle shift eval_at formatter
	global_registry'''.split())


COLORS = {
	'none': (0, 0, 0, 0),
	'black': (0, 0, 0, 1),
	'white': (1, 1, 1, 1),
	'grey': (0.5, 0.5, 0.5, 1),
	'red': (1, 0, 0, 1),
	'green': (0, 1, 0, 1),
	'blue': (0, 0, 1, 1),
	'cyan': (0, 1, 1, 1),
	'yellow': (1, 1, 0, 1),
	'magenta': (1, 0, 1, 1),
	'purple': (0.5, 0, 0.5, 1),
}

COLORS['transparent'] = COLORS['none']
COLORS['w'] = COLORS['white']
COLORS['k'] = COLORS['black']
COLORS['r'] = COLORS['red']
COLORS['g'] = COLORS['green']
COLORS['b'] = COLORS['blue']
COLORS['c'] = COLORS['cyan']
COLORS['m'] = COLORS['magenta']
COLORS['y'] = COLORS['yellow']


global_registry = []


def angle(t, start_angle=0):
	return t * 2 * pi + start_angle


def shift(t, move):
	return (t + move) % 1


def mirror(t):
	return 1 - abs(t * 2 - 1)


def eval_at(f, t):
	if callable(f):
		return f(t)
	else:
		return f


def formatter(s):
	return s.__mod__


def linspace(start, stop, num=51):
	def do():
		diff = stop - start
		for i in xrange(num):
			yield start + diff * i / (num - 1)
	return list(do())


def obj_to_rgba(s):
	if s in COLORS:
		return COLORS[s]
	if str(s).startswith('#'):
		n = int(s[1:], 16)
		if len(s) == 7:
			return (n >> 24 / 255., ((n >> 16) & 0xFF) / 255., (n & 0xFF) / 255., 1)
		elif len(s) == 9:
			return (n >> 32 / 255., ((n >> 24) & 0xFF) / 255., ((n >> 8) & 0xFF) / 255., (n & 0xFF) / 255.)
	return s


class Plotter:
	def __init__(self):
		self.width = 512
		self.height = 512
		self.win = [-1, -1, 1, 1]
		self.nframes = 25
		self.nsteps = 51

	def set_resolution(self, x, y):
		self.width = x
		self.height = y

	def set_window(self, minx, miny, maxx, maxy):
		self.win = [minx, miny, maxx, maxy]

	def set_frames(self, n):
		self.nframes = n

	def set_steps(self, n):
		self.nsteps = n

	def _create_cairo(self):
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
		ctx = cairo.Context(surface)
		ctx.translate((self.win[0] + self.win[2]) / 2, (self.win[1] + self.win[3]) / 2)
		ctx.scale(self.width / (self.win[2] - self.win[0]), self.height / (self.win[3] - self.win[1]))
		ctx.translate(-(self.win[0] + self.win[2]) / 2, -(self.win[1] + self.win[3]) / 2)
		ctx.translate((self.win[2] - self.win[0]) / 2, (self.win[3] - self.win[1]) / 2)
		return surface, ctx

	def _draw(self, objs, frame_cb, t_start=0, t_end=1):
		objs = [obj for obj in objs if obj.visible]

		t_values = linspace(t_start, t_end, self.nsteps)
		for i in xrange(self.nframes):
			bound = 1 + ceil((len(t_values) - 1) * i / (self.nframes - 1))
			bound = int(bound)
			ts = t_values[:bound]
			surface, ctx = self._create_cairo()
			for obj in objs:
				obj.draw(ts, ctx)
			frame_cb(surface, ctx, i)

	def save_png(self, objs, pattern, t_start=0, t_end=1):
		def save(surface, ctx, i):
			surface.write_to_png('%s-%03d.png' % (pattern, i))
		self._draw(objs, save, t_start, t_end)

	def save_gif(self, objs, f, delay=100, t_start=0, t_end=1):
		def save(surface, ctx, i):
			png = os.path.join(tmp, '%06d.png' % i)
			surface.write_to_png(png)
			files.append(png)

		files = []
		tmp = tempfile.mkdtemp()
		try:
			self._draw(objs, save, t_start, t_end)
			subprocess.call(['convert', '-loop', '0', '-dispose', 'previous', '-delay', str(delay)] + files + [f])
		finally:
			shutil.rmtree(tmp)


class Drawable(object):
	def __init__(self, fill_color='none', border_color='black', border_width=None, hidden=False, register=True):
		self.fill_color = obj_to_rgba(fill_color)
		self.border_color = obj_to_rgba(border_color)
		self.border_width = border_width or 0.01

		self.visible = not hidden
		if register:
			global_registry.append(self)

	def draw(self, ts, ctx):
		raise NotImplementedError()


class Background(Drawable):
	def __init__(self, color='none', **kw):
		super(Background, self).__init__(**kw)
		self.color = obj_to_rgba(color)

	def draw(self, ts, ctx):
		ctx.set_source_rgba(*self.color)
		ctx.paint()


class Circle(Drawable):
	def __init__(self, center, radius, full=True, angle=angle, sweep_start=None, sweep_end=None, **kw):
		super(Circle, self).__init__(**kw)

		self._center = center
		self._radius = radius
		self._angle = angle
		self._sweep_start = sweep_start
		self._sweep_end = sweep_end
		self.full = full

	def center(self, t):
		return eval_at(self._center, t)

	def radius(self, t):
		return eval_at(self._radius, t)

	def angle(self, t):
		return eval_at(self._angle, t)

	def sweep_start(self, t):
		return eval_at(self._sweep_start, t)

	def sweep_start_value(self, t):
		c = self.center(t)
		r = self.radius(t)
		return (cos(self.sweep_start(t)) * r + c[0], sin(self.sweep_start(t)) * r + c[1])

	def sweep_end(self, t):
		return eval_at(self._sweep_end, t)

	def sweep_end_value(self, t):
		c = self.center(t)
		r = self.radius(t)
		return (cos(self.sweep_end(t)) * r + c[0], sin(self.sweep_end(t)) * r + c[1])

	def draw(self, ts, ctx):
		c = self.center(ts[-1])
		r = self.radius(ts[-1])

		if self.full:
			start, end = self.angle(0), self.angle(1)
		elif self._sweep_start and self._sweep_end:
			start, end = self.sweep_start(ts[-1]), self.sweep_end(ts[-1])
		else:
			start, end = self.angle(ts[0]), self.angle(ts[-1])

		if start <= end:
			ctx.arc(c[0], c[1], r, start, end)
		else:
			ctx.arc_negative(c[0], c[1], r, start, end)

		ctx.set_line_width(self.border_width)
		ctx.set_source_rgba(*self.fill_color)
		ctx.fill_preserve()
		ctx.set_source_rgba(*self.border_color)
		ctx.stroke()

	def value(self, t):
		c = self.center(t)
		r = self.radius(t)
		return (cos(self.angle(t)) * r + c[0], sin(self.angle(t)) * r + c[1])


class Dot(Circle):
	def __init__(self, center, color='black', fill=True):
		fill_color = fill and color or 'none'
		super(Dot, self).__init__(center=center, radius=0.05, fill_color=fill_color, border_color=color)


class Line(Drawable):
	def __init__(self, p1, p2, color='black', **kw):
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

	def draw(self, ts, ctx):
		p1 = self.p1(ts[-1])
		p2 = self.p2(ts[-1])

		ctx.set_line_width(self.border_width)
		ctx.set_source_rgba(*self.border_color)
		ctx.move_to(p1[0], p1[1])
		ctx.line_to(p2[0], p2[1])
		ctx.stroke()


class Graph(Drawable):
	def __init__(self, f, **kw):
		super(Graph, self).__init__(**kw)
		self._f = f
	
	def value(self, t):
		return self._f(t)

	def draw(self, ts, ctx):
		# TODO be smarter for the number of points and placement/density of points
		first = True
		for t in ts:
			if first:
				ctx.move_to(*self._f(t))
			else:
				ctx.line_to(*self._f(t))
			first = False

		ctx.set_line_width(self.border_width)
		ctx.set_source_rgba(*self.fill_color)
		ctx.fill_preserve()
		ctx.set_source_rgba(*self.border_color)
		ctx.stroke()


class Label(Drawable):
	def __init__(self, text, pos, size=1, **kw):
		super(Label, self).__init__(**kw)
		self._text = text
		self._size = size
		self._pos = pos

	def draw(self, ts, ctx):
		ctx.move_to(*eval_at(self._pos, ts[-1]))
		ctx.set_font_size(eval_at(self._size, ts[-1]))
		ctx.set_source_rgba(*self.fill_color)
		ctx.show_text(eval_at(self._text, ts[-1]))
		ctx.fill()


def run_file(opts):
	plotter = Plotter()
	plotter.set_window(*opts.zone)
	plotter.set_resolution(*opts.size)
	plotter.set_frames(opts.frames)

	g = globals()
	vars = dict((k, g[k]) for k in __all__)
	vars['plotter'] = plotter
	module = execfile(opts.input, vars, vars)

	if opts.output.endswith('.gif'):
		plotter.save_gif(global_registry, opts.output, delay=opts.delay)
	else:
		plotter.save_png(global_registry, opts.output)


def main():
	argparser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
	argparser.add_argument('input', metavar='FILE')
	argparser.add_argument('output', metavar='OUTPUT')
	argparser.add_argument('--zone', metavar='X,Y,X,Y', help='virtual canvas zone shown by the output image', default='-2,-2,2,2')
	argparser.add_argument('--size', metavar='WxH', help='size of output image', default='512x512')
	argparser.add_argument('-n', '--frames', metavar='FRAMES', help='number of frames', type=int, default=25)
	argparser.add_argument('-d', '--delay', metavar='MS', help='delay between frames (in ms)', type=int, default=50)
	opts = argparser.parse_args()

	if not opts.output:
		opts.output = os.path.splitext(opts.geomfile)[0] + '.gif'

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
