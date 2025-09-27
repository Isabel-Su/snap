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
ax.plot(elapsed, tpi, 'b-', label='Team Performance Index (TPI)')
ax.plot(elapsed, ppi, 'r--', label='Player Performance Index (PPI)')

ax.set_title("Microeconomy Impact Chart")
ax.set_xlabel("Game Time (MM:SS elapsed)")
ax.set_ylabel("Performance Index")
# Apply major/minor locators and formatters to avoid label crowding
ax.xaxis.set_major_locator(MultipleLocator(major_step))
ax.xaxis.set_major_formatter(FuncFormatter(mmss_formatter))
ax.xaxis.set_minor_locator(MultipleLocator(minor_step))
ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_xticks(range(start, end + 1, minor_step), minor=True)
ax.tick_params(axis='x', which='major', length=7)
ax.tick_params(axis='x', which='minor', length=3)
plt.setp(ax.get_xticklabels(), rotation=45)
ax.grid(alpha=0.3)
ax.legend()

output_path = 'impact_chart.png'
plt.tight_layout()
plt.savefig(output_path, dpi=150)
print(f"Saved impact chart to {output_path}")
print('Tick range (s elapsed):', start, 'to', end)
print('Major tick step (s):', major_step, 'Minor tick step (s):', minor_step)

# Only call plt.show() when running with an interactive backend. In headless
# environments (Agg), plt.show() will either do nothing or raise errors if a
# GUI backend isn't available, so we avoid calling it there.
current_backend = matplotlib.get_backend()
if current_backend in matplotlib.rcsetup.interactive_bk:
	try:
		plt.show()
	except Exception as e:
		print(f"plt.show() failed with backend {current_backend}: {e}")
else:
	print(f"Not calling plt.show() because backend '{current_backend}' is non-interactive. Plot saved to {output_path}.")