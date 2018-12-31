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


__all__ = [
	'cos', 'sin', 'tan', 'pi', 'e', 'fmod', 'ceil', 'floor', 'mirror',
	'Plotter', 'Circle', 'Dot', 'Line', 'Graph', 'Drawable', 'Label', 'Background',
	'angle', 'shift', 'eval_at', 'formatter',
	'global_registry'
]


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
		for i in range(num):
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


if sys.version_info.major < 3:
	range = xrange
else:
	def execfile(path, globals):
		"""Exec Python `file` with `globals` as in Python 2"""
		with open(path) as fd:
			src = fd.read()
		code = compile(src, path, 'exec')
		exec(code, globals)  # pylint: disable=exec-used


class Plotter:
	def __init__(self):
		self.width = 512
		self.height = 512
		self.win = [-1, -1, 1, 1]
		self.nframes = 25

	def set_resolution(self, x, y):
		self.width = x
		self.height = y

	def set_window(self, minx, miny, maxx, maxy):
		self.win = [minx, miny, maxx, maxy]

	def set_frames(self, n):
		self.nframes = n

	def _create_cairo(self):
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
		ctx = cairo.Context(surface)
		ctx.translate((self.win[0] + self.win[2]) / 2, (self.win[1] + self.win[3]) / 2)
		ctx.scale(self.width / (self.win[2] - self.win[0]), self.height / (self.win[3] - self.win[1]))
		ctx.translate(-(self.win[0] + self.win[2]) / 2, -(self.win[1] + self.win[3]) / 2)
		ctx.translate((self.win[2] - self.win[0]) / 2, (self.win[3] - self.win[1]) / 2)
		return surface, ctx

	def _draw(self, objs, t_start=0, t_end=1):
		precision = (self.win[2] - self.win[0]) / self.width
		precision = min(precision, (self.win[3] - self.win[1]) / self.height)

		objs = [obj for obj in objs if obj.visible]

		t_values = linspace(t_start, t_end, self.nframes)
		for f_end in t_values:
			surface, ctx = self._create_cairo()
			for obj in objs:
				obj.draw(ctx, t_start, f_end, precision=precision)
			yield (surface, ctx)

	def save_png(self, objs, pattern, t_start=0, t_end=1):
		for i, (surface, ctx) in enumerate(self._draw(objs, t_start, t_end)):
			surface.write_to_png('%s-%03d.png' % (pattern, i))

	def save_gif(self, objs, f, delay=100, t_start=0, t_end=1):
		files = []
		tmp = tempfile.mkdtemp()
		try:
			for i, (surface, ctx) in enumerate(self._draw(objs, t_start, t_end)):
				png = os.path.join(tmp, '%06d.png' % i)
				surface.write_to_png(png)
				files.append(png)

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

	def draw(self, ctx, t_start, t_end, **kwargs):
		# kwargs:
		# precision: a drawable may adapt its drawing so lines length do not exceed this value
		raise NotImplementedError()


class Background(Drawable):
	def __init__(self, color='none', **kw):
		super(Background, self).__init__(**kw)
		self.color = obj_to_rgba(color)

	def draw(self, ctx, t_start, t_end, **kwargs):
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

	def draw(self, ctx, t_start, t_end, **kwargs):
		c = self.center(t_end)
		r = self.radius(t_end)

		if self.full:
			start, end = self.angle(0), self.angle(1)
		elif self._sweep_start and self._sweep_end:
			start, end = self.sweep_start(t_end), self.sweep_end(t_end)
		else:
			start, end = self.angle(t_start), self.angle(t_end)

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

	def draw(self, ctx, t_start, t_end, **kwargs):
		p1 = self.p1(t_end)
		p2 = self.p2(t_end)

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

	def draw(self, ctx, t_start, t_end, **kwargs):
		t = t_start
		first_point = True
		step = (t_end - t_start) / 2
		precision = kwargs.pop('precision', 1)

		while t < t_end:
			if first_point:
				point = self._f(t)
				ctx.move_to(*point)
			else:
				# use smaller steps if 2 consecutive points may be too far apart
				# TODO it's not useful to do small steps if points are on a line anyway
				while True:
					new_t = min(t_end, t + step)
					new_point = self._f(new_t)

					distance = abs(complex(*new_point) - complex(*point))
					if distance < precision:
						break

					step /= 2

				t = new_t
				point = new_point
				ctx.line_to(*point)
				# TODO avoid expensive re-computation by painting over previous frames (per obj)?
				# for obj in objs: obj.draw(previous_frame, current_frame, frame_data[obj])
				# flatten frame_data

			first_point = False

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

	def draw(self, ctx, t_start, t_end, **kwargs):
		ctx.move_to(*eval_at(self._pos, t_end))
		ctx.set_font_size(eval_at(self._size, t_end))
		ctx.set_source_rgba(*self.fill_color)
		ctx.show_text(eval_at(self._text, t_end))
		ctx.fill()


def run_file(opts):
	plotter = Plotter()
	plotter.set_window(*opts.zone)
	plotter.set_resolution(*opts.size)
	plotter.set_frames(opts.frames)

	g = globals()
	vars = dict((k, g[k]) for k in __all__)
	vars['plotter'] = plotter
	execfile(opts.input, vars)

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
		zone = [float(x) for x in zone]
	except ValueError:
		argparser.error('zone argument should be if X,Y,X,Y format')
	opts.zone = zone

	size = opts.size.split('x')
	if len(size) != 2:
		argparser.error('size argument should be if WxH format')
	try:
		size = [int(x) for x in size]
	except ValueError:
		argparser.error('size argument should be if WxH format')
	opts.size = size

	run_file(opts)


if __name__ == '__main__':
	main()
