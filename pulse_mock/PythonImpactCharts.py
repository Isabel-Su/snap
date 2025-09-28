import os
import math
import matplotlib
# Select a backend dynamically:
# - prefer an interactive backend when available (so plt.show() works)
# - if none available (headless/CI), fall back to 'Agg' which is non-interactive but can save files
interactive_backends = matplotlib.rcsetup.interactive_bk
backend = matplotlib.get_backend()
is_interactive = backend in interactive_backends

if not is_interactive:
	# try common interactive backends
	for candidate in ('MacOSX', 'Qt5Agg', 'TkAgg', 'QtAgg', 'GTK3Agg'):
		try:
			matplotlib.use(candidate, force=True)
			backend = matplotlib.get_backend()
			is_interactive = backend in interactive_backends
			if is_interactive:
				break
		except Exception:
			# backend not available, try next
			continue

if not is_interactive:
	# final fallback to Agg for headless environments
	matplotlib.use('Agg', force=True)

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter, NullFormatter
import matplotlib.animation as animation
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

# compute elapsed seconds (since game start) for each play
elapsed = [3600 - p['game_seconds_remaining'] for p in plays]
# y-series: use qb_epa for TPI and wpa for PPI as example proxies
tpi = [p.get('qb_epa', 0.0) for p in plays]
ppi = [p.get('wpa', 0.0) for p in plays]

# Ensure the points are ordered by elapsed time so the animated line
# doesn't draw strange connectors between out-of-order points.
combined = list(zip(elapsed, tpi, ppi))
if combined:
	combined.sort(key=lambda x: x[0])
	elapsed, tpi, ppi = [list(col) for col in zip(*combined)]
else:
	elapsed, tpi, ppi = [], [], []

# Pre-compute y-axis limits (with a small padding) so matplotlib does not
# autoscale between frames and cause visual jumps during the animation.
if tpi or ppi:
	all_y = []
	if tpi:
		all_y.extend(tpi)
	if ppi:
		all_y.extend(ppi)
	ymin = min(all_y)
	ymax = max(all_y)
	# If flat line, provide a reasonable default padding
	if math.isclose(ymin, ymax):
		pad = max(0.5, abs(ymin) * 0.1)
	else:
		pad = (ymax - ymin) * 0.12
else:
	ymin, ymax, pad = -1.0, 1.0, 0.5

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
ax.set_xlim(start, end)
ax.set_ylim(ymin - pad, ymax + pad)
ax.tick_params(axis='x', which='major', length=7)
ax.tick_params(axis='x', which='minor', length=3)
plt.setp(ax.get_xticklabels(), rotation=45)
ax.grid(alpha=0.3)

# Start with empty lines and update them over time
line_tpi, = ax.plot([], [], 'b-', label='Team Performance Index (TPI)')
line_ppi, = ax.plot([], [], 'r--', label='Player Performance Index (PPI)')
marker, = ax.plot([], [], 'ko', ms=6)
ax.legend()

output_path = 'impact_chart.png'

def init():
	line_tpi.set_data([], [])
	line_ppi.set_data([], [])
	marker.set_data([], [])
	return line_tpi, line_ppi, marker

def update(i):
	# update lines to include data up to index i
	x = elapsed[: i + 1]
	y1 = tpi[: i + 1]
	y2 = ppi[: i + 1]
	line_tpi.set_data(x, y1)
	line_ppi.set_data(x, y2)
	# place a marker on the most recent point of the primary series
	if x:
		marker.set_data(x[-1], y1[-1])
	return line_tpi, line_ppi, marker

# Animation: prefer interactive display; if headless, render updates and save final image
current_backend = matplotlib.get_backend()
is_interactive = current_backend in matplotlib.rcsetup.interactive_bk

frame_interval_ms = 2000  # milliseconds between frames (0.5s)

if is_interactive:
	# Turn on interactive mode so the GUI event loop processes between frames.
	plt.ion()
	ani = animation.FuncAnimation(
		fig,
		update,
		frames=len(elapsed),
		init_func=init,
		interval=frame_interval_ms,
		blit=False,
		repeat=False,
	)
	try:
		# Show window without blocking — we'll drive the event loop with plt.pause
		plt.show(block=False)
		# Let the animation run by yielding to the GUI event loop at the frame interval
		for _ in range(len(elapsed)):
			plt.pause(frame_interval_ms / 1000.0)
		# Keep the window open briefly after finishing
		plt.pause(5)
	except Exception as e:
		print(f"Interactive display failed with backend {current_backend}: {e}")
else:
	# Headless: step through frames to simulate live updates, then save final image
	for i in range(len(elapsed)):
		update(i)
		# draw on the Agg canvas
		fig.canvas.draw()
		# sleep to simulate live arrival (use same interval as interactive)
		time.sleep(frame_interval_ms / 1000.0)
	plt.tight_layout()
	plt.savefig(output_path, dpi=150)
	print(f"Saved impact chart to {output_path}")
	print('Tick range (s elapsed):', start, 'to', end)
	print('Major tick step (s):', major_step, 'Minor tick step (s):', minor_step)