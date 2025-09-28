import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from io import BytesIO
from flask import Flask, send_file, request, jsonify, make_response, Response
import tempfile
import threading
import time
import json
from matplotlib.ticker import MultipleLocator, FuncFormatter, NullFormatter
import matplotlib.animation as animation
from matplotlib.widgets import RadioButtons, TextBox, Button

# Dropdown was added in newer matplotlib versions. Provide a small
# fallback implementation that mimics the Dropdown API (on_select)
# using a Button which cycles through options when Dropdown isn't
# available. This lets the UI remain usable on older matplotlib.
try:
	from matplotlib.widgets import Dropdown
except Exception:
	class Dropdown:
		def __init__(self, ax, items, active=0):
			self._items = list(items)
			self._active = int(active)
			self._callbacks = []
			# use a simple Button to display current selection and cycle
			self._btn = Button(ax, self._items[self._active])
			self._btn.on_clicked(self._on_click)

		def _on_click(self, event):
			# cycle forward
			self._active = (self._active + 1) % len(self._items)
			label = self._items[self._active]
			# update button label
			try:
				self._btn.label.set_text(label)
			except Exception:
				pass
			# notify callbacks
			for cb in self._callbacks:
				try:
					cb(label)
				except Exception:
					pass

		def on_select(self, callback):
			# register a callback that accepts the selected label
			self._callbacks.append(callback)

		def set_val(self, label):
			# programmatically set value (used by TextBox.set_val flow)
			if label in self._items:
				self._active = self._items.index(label)
				try:
					self._btn.label.set_text(label)
				except Exception:
					pass
import time

plt.style.use("fivethirtyeight")

# Use the plays data and create an elapsed-time x axis with 60s ticks
plays = [
	{"game_seconds_remaining": 3409.0, "qb_epa": 0.552650292403996, "wpa": 0.0292352437973022},
	{"game_seconds_remaining": 3249.0, "qb_epa": 0.190153431612998, "wpa": 0.0016123950481414},
	{"game_seconds_remaining": 2652.0, "qb_epa": 0.555401087272912, "wpa": 0.0147861838340759},
	{"game_seconds_remaining": 2568.0, "qb_epa": -0.285567590035498, "wpa": -0.0037904381752014},
	{"game_seconds_remaining": 2521.0, "qb_epa": 1.28535311296582, "wpa": 0.0119984149932861},
	{"game_seconds_remaining": 2479.0, "qb_epa": -0.430872592609376, "wpa": 0.0031712353229522},
	{"game_seconds_remaining": 1920.0, "qb_epa": -0.515209543053061, "wpa": -0.0262914001941681},
	{"game_seconds_remaining": 1913.0, "qb_epa": 3.72801848780364, "wpa": 0.153878569602966},
	{"game_seconds_remaining": 1880.0, "qb_epa": -0.401088450045791, "wpa": -0.0135473608970642},
	{"game_seconds_remaining": 1876.0, "qb_epa": 0.675303220981732, "wpa": 0.0184066891670227},
	{"game_seconds_remaining": 1869.0, "qb_epa": 0.511088427563664, "wpa": 0.0012808442115783},
	{"game_seconds_remaining": 1795.0, "qb_epa": 0.0729459878057241, "wpa": 0.0003869533538818},
	{"game_seconds_remaining": 1752.0, "qb_epa": 0.731964903650805, "wpa": 0.0195994973182678},
	{"game_seconds_remaining": 1719.0, "qb_epa": -0.258798455586657, "wpa": -0.0113470554351807},
	{"game_seconds_remaining": 1502.0, "qb_epa": -2.0366979597602, "wpa": -0.0663243532180786},
	{"game_seconds_remaining": 1456.0, "qb_epa": -1.51156951696861, "wpa": -0.0221386551856995},
	{"game_seconds_remaining": 1142.0, "qb_epa": -0.789402016904205, "wpa": -0.0237884521484375},
	{"game_seconds_remaining": 886.0, "qb_epa": 0.539945995435119, "wpa": 0.0156305432319641},
	{"game_seconds_remaining": 621.0, "qb_epa": 0.363901168340817, "wpa": 0.0197494029998779},
	{"game_seconds_remaining": 586.0, "qb_epa": 0.368475484661758, "wpa": 0.0027300715446472},
	{"game_seconds_remaining": 506.0, "qb_epa": -0.825948749668896, "wpa": -0.0326569676399231},
	{"game_seconds_remaining": 498.0, "qb_epa": -0.44213400199078, "wpa": 0.0102556347846985},
	{"game_seconds_remaining": 235.0, "qb_epa": -0.565623112954199, "wpa": -0.0481255054473877},
	{"game_seconds_remaining": 111.0, "qb_epa": 0.0784624250954948, "wpa": 0.0168435573577881},
]

def format_mmss(sec):
	m = int(sec) // 60
	s = int(sec) % 60
	return f"{m:02d}:{s:02d}"

# compute elapsed seconds (since game start) for each play and ordering index
elapsed = [3600 - p['game_seconds_remaining'] for p in plays]
# We'll animate in chronological order (by elapsed) to avoid connecting
# out-of-order points which causes visual artifacts.
idx_order = sorted(range(len(plays)), key=lambda i: elapsed[i])

# Helper to extract a numeric series by variable name. Supports special
# names: 'elapsed' and 'diff' (wpa - qb_epa). Falls back to 0.0 for missing values.
def get_series(var_name):
	if var_name == 'elapsed':
		return [elapsed[i] for i in idx_order]
	#if var_name == 'diff':
		#return [float(plays[i].get('wpa') or 0.0) - float(plays[i].get('qb_epa') or 0.0) for i in idx_order]
	# generic numeric field
	return [float(plays[i].get(var_name) or 0.0) for i in idx_order]

# Define three graph presets (initially the same 'tpi vs diff' per your request).
presets = [
	{'label': 'Jalen Hurts', 'x': 'elapsed', 'y': 'qb_epa'},
	{'label': 'Smith', 'x': 'elapsed', 'y': 'qb_epa'},
	{'label': 'Brown', 'x': 'elapsed', 'y': 'qb_epa'},
]

# Active selection state
active_idx = 0

# Current series (will be populated from presets)
xs = get_series(presets[active_idx]['x'])
ys = get_series(presets[active_idx]['y'])

# Pre-compute axis limits (these will be recomputed when variables change)
def compute_limits(xseries, yseries):
	if xseries:
		min_x, max_x = min(xseries), max(xseries)
	else:
		min_x, max_x = 0.0, 1.0
	if yseries:
		min_y, max_y = min(yseries), max(yseries)
	else:
		min_y, max_y = -1.0, 1.0
	if math.isclose(min_y, max_y):
		pad = max(0.5, abs(min_y) * 0.1)
	else:
		pad = (max_y - min_y) * 0.12
	return (min_x, max_x), (min_y - pad, max_y + pad)


(xlim, ylim) = compute_limits(xs, ys)
# initial diff series (wpa - qb_epa) following idx_order
diff_series = [float(plays[i].get('wpa') or 0.0) - float(plays[i].get('qb_epa') or 0.0) for i in idx_order]

min_e, max_e = min(elapsed), max(elapsed)
# Create tick range bounds
start = int(math.floor(min_e / 60.0) * 60)
end = int(math.ceil(max_e / 60.0) * 60)
if start == end:
	end = start + 60

# We'll use major ticks every 5 minutes (300s) with labels and minor ticks every 60s
major_step = 300  # seconds (5 minutes)
minor_step = 60   # seconds (1 minute)

# Formatter for MM:SS
def mmss_formatter(x, pos=None):
	try:
		return format_mmss(int(x))
	except Exception:
		return ''

fig, ax = plt.subplots(figsize=(10, 4.5))
# Prepare the figure and animated lines
ax.set_title("Player Impact Chart")
ax.set_xlabel("Game Time (MM:SS elapsed)")
ax.set_ylabel("Performance Index")
# Apply major/minor locators and formatters to avoid label crowding
ax.xaxis.set_major_locator(MultipleLocator(major_step))
ax.xaxis.set_major_formatter(FuncFormatter(mmss_formatter))
ax.xaxis.set_minor_locator(MultipleLocator(minor_step))
ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_xticks(range(start, end + 1, minor_step), minor=True)
# Fix x/y limits before starting animation to avoid autoscale artifacts
# use computed limits for the currently selected preset
ax.set_xlim(xlim[0], xlim[1])
ax.set_ylim(ylim[0], ylim[1])
# If the x-axis represents elapsed seconds, apply the MM:SS formatter and ticks
if presets[active_idx]['x'] == 'elapsed':
	ax.xaxis.set_major_locator(MultipleLocator(major_step))
	ax.xaxis.set_major_formatter(FuncFormatter(mmss_formatter))
	ax.xaxis.set_minor_locator(MultipleLocator(minor_step))
	ax.xaxis.set_minor_formatter(NullFormatter())
	ax.set_xticks(range(start, end + 1, minor_step), minor=True)
else:
	# otherwise let matplotlib choose reasonable ticks
	pass
ax.tick_params(axis='x', which='major', length=7)
ax.tick_params(axis='x', which='minor', length=3)
plt.setp(ax.get_xticklabels(), rotation=45)
ax.grid(alpha=0.3)

# Start with empty lines and update them over time
line_tpi, = ax.plot([], [], 'b-', label='Team Performance Index (TPI)')
line_diff, = ax.plot([], [], 'r--', label='Difference between Team and Performance Index')
marker, = ax.plot([], [], 'ko', ms=6)
ax.legend()

output_path = 'impact_chart.png'

def init():
	line_tpi.set_data([], [])
	line_diff.set_data([], [])
	marker.set_data([], [])
	return line_tpi, line_diff, marker

def update(i):
	# update lines to include data up to index i using the current xs/ys
	x = xs[: i + 1]
	y1 = ys[: i + 1]
	line_tpi.set_data(x, y1)
	line_diff.set_data(x, diff_series[: i + 1])
	# place a marker on the most recent point of the primary series
	if x:
		# marker.set_data expects sequences; wrap single point in lists
		marker.set_data([x[-1]], [y1[-1]])
	return line_tpi, line_diff, marker

frame_interval_ms = 2000  # milliseconds between frames (0.5s)

# --- UI: RadioButtons to pick preset and TextBoxes to edit x/y variables ---
	# create small axes for controls on the right
axcolor = 'lightgoldenrodyellow'
rax = plt.axes([0.87, 0.5, 0.11, 0.05], facecolor=axcolor)
# Dropdown: choose which preset/graph to display
dropdown = Dropdown(rax, [p['label'] for p in presets], active=active_idx)

tbx_x = plt.axes([0.87, 0.35, 0.11, 0.04], facecolor=axcolor)
text_x = TextBox(tbx_x, 'x var', initial=presets[active_idx]['x'])
tbx_y = plt.axes([0.87, 0.27, 0.11, 0.04], facecolor=axcolor)
text_y = TextBox(tbx_y, 'y var', initial=presets[active_idx]['y'])
bax = plt.axes([0.87, 0.2, 0.11, 0.04])
apply_btn = Button(bax, 'Apply')

def apply_preset(event=None):
	global xs, ys, xlim, ylim, ani, active_idx, diff_series
	# update current preset from text boxes
	presets[active_idx]['x'] = text_x.text.strip()
	presets[active_idx]['y'] = text_y.text.strip()
	# recompute series
	xs = get_series(presets[active_idx]['x'])
	ys = get_series(presets[active_idx]['y'])
	# recompute diff series (wpa - qb_epa) relative to idx_order
	diff_series = [float(plays[i].get('wpa') or 0.0) - float(plays[i].get('qb_epa') or 0.0) for i in idx_order]
	(xlim, ylim) = compute_limits(xs, ys)
	ax.set_xlim(xlim[0], xlim[1])
	ax.set_ylim(ylim[0], ylim[1])
	# if x is elapsed, reapply time formatter/ticks
	if presets[active_idx]['x'] == 'elapsed':
		ax.xaxis.set_major_locator(MultipleLocator(major_step))
		ax.xaxis.set_major_formatter(FuncFormatter(mmss_formatter))
		ax.xaxis.set_minor_locator(MultipleLocator(minor_step))
		ax.xaxis.set_minor_formatter(NullFormatter())
		ax.set_xticks(range(start, end + 1, minor_step), minor=True)
	# restart animation with new length
	try:
		ani.event_source.stop()
	except Exception:
		pass
	ani = animation.FuncAnimation(fig, update, frames=len(xs), init_func=init, interval=frame_interval_ms, blit=False, repeat=False)
	plt.draw()

def on_radio(label):
	global active_idx, xs, ys, diff_series, xlim, ylim, ani
	active_idx = next(i for i, p in enumerate(presets) if p['label'] == label)
	# update series to the selected preset
	xs = get_series(presets[active_idx]['x'])
	ys = get_series(presets[active_idx]['y'])
	diff_series = [float(plays[i].get('wpa') or 0.0) - float(plays[i].get('qb_epa') or 0.0) for i in idx_order]
	(xlim, ylim) = compute_limits(xs, ys)
	ax.set_xlim(xlim[0], xlim[1])
	ax.set_ylim(ylim[0], ylim[1])
	# update text boxes to show the selected preset
	text_x.set_val(presets[active_idx]['x'])
	text_y.set_val(presets[active_idx]['y'])
	try:
		ani.event_source.stop()
	except Exception:
		pass
	ani = animation.FuncAnimation(fig, update, frames=len(xs), init_func=init, interval=frame_interval_ms, blit=False, repeat=False)

	# wire dropdown selection to the same handler used for radio buttons
dropdown.on_select(on_radio)
apply_btn.on_clicked(apply_preset)

# Animation: prefer 	interactive display; if headless, render updates and save final image
current_backend = matplotlib.get_backend()
current_backend in matplotlib.rcsetup.interactive_bk

frame_interval_ms = 2000  # milliseconds between frames (0.5s)

	# Turn on interactive mode so the GUI event loop processes between frames.
plt.ion()
ani = animation.FuncAnimation(
	fig,
	update,
	frames=len(xs),
	init_func=init,
	interval=frame_interval_ms,
	blit=False,
	repeat=False,
)
# Skip interactive display when running as a headless server; the Flask
# endpoints below will render PNG/GIF/JSON/SSE instead of showing a GUI.
try:
	# No-op: do not call plt.show() or plt.pause() in server mode.
	pass
except Exception as e:
	print(f"Interactive display skipped: {e}")


# --- ATTACH FLASK ENDPOINTS (headless) ---
app = Flask(__name__)

# helper to render a static png
def render_scroller_png_bytes() -> BytesIO:
	# default uses active_idx
	xs_local, ys_local, diff_local, xlim_local, ylim_local = build_series_for_preset(active_idx)

	fig, ax = plt.subplots(figsize=(10, 4.5))
	fig.subplots_adjust(bottom=0.22)
	ax.set_title("Player Impact Chart")
	ax.set_xlabel("Game Time (MM:SS elapsed)")
	ax.set_ylabel("Performance Index")
	ax.xaxis.set_major_locator(MultipleLocator(major_step))
	ax.xaxis.set_major_formatter(FuncFormatter(mmss_formatter))
	ax.xaxis.set_minor_locator(MultipleLocator(minor_step))
	ax.xaxis.set_minor_formatter(NullFormatter())
	ax.set_xlim(xlim_local[0], xlim_local[1])
	ax.set_ylim(ylim_local[0], ylim_local[1])
	ax.tick_params(axis='x', which='major', length=7)
	ax.tick_params(axis='x', which='minor', length=3)
	plt.setp(ax.get_xticklabels(), rotation=45)
	ax.grid(alpha=0.3)
	ax.plot(xs_local, ys_local, 'b-', label='Primary')
	ax.plot(xs_local, diff_local, 'r--', label='Diff')
	if xs_local:
		ax.plot([xs_local[-1]], [ys_local[-1]], 'ko', ms=6)
	ax.legend()
	buf = BytesIO()
	fig.savefig(buf, format='png', dpi=150)
	plt.close(fig)
	buf.seek(0)
	return buf


# GIF generation
_gif_lock = threading.Lock()
_GIF_DIR = os.path.dirname(__file__)
_gif_cache_path = os.path.join(_GIF_DIR, 'scroller.gif')

def _cache_path_for_interval(interval_ms: int) -> str:
	return os.path.join(_GIF_DIR, f"scroller_{int(interval_ms)}.gif")

def _cache_path_for_preset_interval(preset_label: str, interval_ms: int) -> str:
	safe = preset_label.replace(' ', '_')
	return os.path.join(_GIF_DIR, f"scroller_{safe}_{int(interval_ms)}.gif")


def build_series_for_preset(preset_idx: int):
	# return xs, ys, diff_series, xlim, ylim computed for the preset index
	p = presets[preset_idx]
	xs_local = get_series(p['x'])
	ys_local = get_series(p['y'])
	diff_local = [float(plays[i].get('wpa') or 0.0) - float(plays[i].get('qb_epa') or 0.0) for i in idx_order]
	xlim_local, ylim_local = compute_limits(xs_local, ys_local)
	return xs_local, ys_local, diff_local, xlim_local, ylim_local

def generate_scroller_gif(path: str, interval_ms: int = 600):
	fig, ax = plt.subplots(figsize=(10, 4.5))
	fig.subplots_adjust(bottom=0.22)
	ax.set_title("Player Impact Chart")
	ax.set_xlabel("Game Time (MM:SS elapsed)")
	ax.set_ylabel("Performance Index")
	ax.xaxis.set_major_locator(MultipleLocator(major_step))
	ax.xaxis.set_major_formatter(FuncFormatter(mmss_formatter))
	ax.xaxis.set_minor_locator(MultipleLocator(minor_step))
	ax.xaxis.set_minor_formatter(NullFormatter())
	ax.set_xlim(xlim[0], xlim[1])
	ax.set_ylim(ylim[0], ylim[1])
	ax.grid(alpha=0.3)
	line_primary, = ax.plot([], [], 'b-', label='Primary')
	line_diff, = ax.plot([], [], 'r--', label='Diff')
	marker, = ax.plot([], [], 'ko', ms=6)
	ax.legend()

	def init_anim():
		line_primary.set_data([], [])
		line_diff.set_data([], [])
		marker.set_data([], [])
		return line_primary, line_diff, marker

	def update_anim(i):
		x = xs[: i + 1]
		y1 = ys[: i + 1]
		y2 = diff_series[: i + 1]
		line_primary.set_data(x, y1)
		line_diff.set_data(x, y2)
		if x:
			marker.set_data([x[-1]], [y1[-1]])
		return line_primary, line_diff, marker

	frames = len(xs)
	ani = animation.FuncAnimation(fig, update_anim, frames=frames, init_func=init_anim, interval=interval_ms, blit=False, repeat=False)
	fps = max(0.05, 1000.0 / float(interval_ms))
	writer = PillowWriter(fps=fps)
	os.makedirs(os.path.dirname(path), exist_ok=True)
	ani.save(path, writer=writer)
	plt.close(fig)


@app.route('/scroller.png')
def scroller_png():
	buf = render_scroller_png_bytes()
	return send_file(buf, mimetype='image/png', as_attachment=False, download_name='scroller.png')


@app.route('/scroller.gif')
def scroller_gif():
	interval_raw = request.args.get('interval_ms')
	if interval_raw is None:
		interval_ms = 600
		cache_path = _gif_cache_path
	else:
		try:
			interval_ms = int(interval_raw)
		except Exception:
			interval_ms = 600
		interval_ms = max(50, min(20000, interval_ms))
		cache_path = _cache_path_for_interval(interval_ms)

	# support preset selection
	preset_raw = request.args.get('preset')
	preset_idx = active_idx
	preset_label = presets[preset_idx]['label']
	if preset_raw is not None:
		try:
			preset_idx = int(preset_raw)
			if not (0 <= preset_idx < len(presets)):
				preset_idx = active_idx
		except Exception:
			for i, p in enumerate(presets):
				if p['label'].lower() == preset_raw.lower():
					preset_idx = i
					break
		preset_label = presets[preset_idx]['label']

	# choose cache path per preset+interval
	if interval_raw is None:
		cache_path = _gif_cache_path
	else:
		cache_path = _cache_path_for_preset_interval(preset_label, interval_ms)

	if os.path.exists(cache_path):
		return send_file(cache_path, mimetype='image/gif')

	with _gif_lock:
		if os.path.exists(cache_path):
			return send_file(cache_path, mimetype='image/gif')
		try:
			fd, tmp_path = tempfile.mkstemp(suffix='.gif', dir=os.path.dirname(cache_path))
			os.close(fd)
			# temporarily set global active_idx so generator uses preset
			old_idx = active_idx
			try:
				globals()['active_idx'] = preset_idx
				generate_scroller_gif(tmp_path, interval_ms=interval_ms)
			finally:
				globals()['active_idx'] = old_idx
			os.replace(tmp_path, cache_path)
			return send_file(cache_path, mimetype='image/gif')
		except Exception:
			try:
				if os.path.exists(tmp_path):
					os.unlink(tmp_path)
			except Exception:
				pass
			raise


@app.route('/scroller.json')
def scroller_json():
	# accept optional preset param
	preset_raw = request.args.get('preset')
	preset_idx = active_idx
	if preset_raw is not None:
		try:
			preset_idx = int(preset_raw)
			if not (0 <= preset_idx < len(presets)):
				preset_idx = active_idx
		except Exception:
			for i, p in enumerate(presets):
				if p['label'].lower() == preset_raw.lower():
					preset_idx = i
					break

	xs_local, ys_local, diff_local, xlim_local, ylim_local = build_series_for_preset(preset_idx)
	payload = {
		'elapsed': xs_local,
		'primary': ys_local,
		'diff': diff_local,
		'start': int(math.floor(min(xs_local) / 60.0) * 60) if xs_local else start,
		'end': int(math.ceil(max(xs_local) / 60.0) * 60) if xs_local else end,
		'ymin': ylim_local[0],
		'ymax': ylim_local[1],
		'presets': [p['label'] for p in presets],
		'active': preset_idx,
	}
	resp = make_response(jsonify(payload))
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp


@app.route('/scroller/stream')
def scroller_stream():
	interval_raw = request.args.get('interval_ms', '500')
	try:
		interval_ms = int(interval_raw)
	except Exception:
		interval_ms = 500
	interval_ms = max(50, min(20000, interval_ms))

	# allow preset selection for stream
	preset_raw = request.args.get('preset')
	preset_idx = active_idx
	if preset_raw is not None:
		try:
			preset_idx = int(preset_raw)
			if not (0 <= preset_idx < len(presets)):
				preset_idx = active_idx
		except Exception:
			for i, p in enumerate(presets):
				if p['label'].lower() == preset_raw.lower():
					preset_idx = i
					break

	xs_local, ys_local, diff_local, xlim_local, ylim_local = build_series_for_preset(preset_idx)

	def generate():
		for i in range(len(xs_local)):
			payload = {'i': i, 'elapsed': xs_local[i], 'primary': ys_local[i], 'diff': diff_local[i]}
			yield f"data: {json.dumps(payload)}\n\n"
			time.sleep(interval_ms / 1000.0)
		yield "event: done\ndata: {}\n\n"

	headers = {
		'Cache-Control': 'no-cache',
		'Content-Type': 'text/event-stream',
		'Access-Control-Allow-Origin': '*',
	}
	return Response(generate(), headers=headers)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8001)
