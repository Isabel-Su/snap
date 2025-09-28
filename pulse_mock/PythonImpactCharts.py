import os
import math
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter, NullFormatter
import matplotlib.animation as animation

plt.style.use("fivethirtyeight")

# --- Sample plays data ---
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

# --- Formatting helpers ---
def format_mmss(sec):
    m = int(sec) // 60
    s = int(sec) % 60
    return f"{m:02d}:{s:02d}"

# Compute elapsed (x-axis) and series
elapsed = [3600 - p['game_seconds_remaining'] for p in plays]
tpi = [p.get('qb_epa', 0.0) for p in plays]
ppi = [p.get('wpa', 0.0) for p in plays]

# Ensure chronological order
combined = sorted(zip(elapsed, tpi, ppi), key=lambda x: x[0])
elapsed, tpi, ppi = [list(col) for col in zip(*combined)]

# Axis ranges
all_y = tpi + ppi
ymin, ymax = min(all_y), max(all_y)
pad = (ymax - ymin) * 0.12 if ymax != ymin else 0.5

min_e, max_e = min(elapsed), max(elapsed)
start = int(math.floor(min_e / 60.0) * 60)
end = int(math.ceil(max_e / 60.0) * 60)
if start == end:
    end = start + 60

# --- Build plot ---
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.set_title("Microeconomy Impact Chart")
ax.set_xlabel("Game Time (MM:SS elapsed)")
ax.set_ylabel("Performance Index")
ax.set_xlim(start, end)
ax.set_ylim(ymin - pad, ymax + pad)

ax.xaxis.set_major_locator(MultipleLocator(300))
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: format_mmss(int(x))))
ax.xaxis.set_minor_locator(MultipleLocator(60))
ax.xaxis.set_minor_formatter(NullFormatter())
ax.tick_params(axis='x', which='major', length=7)
ax.tick_params(axis='x', which='minor', length=3)
plt.setp(ax.get_xticklabels(), rotation=45)
ax.grid(alpha=0.3)

line_tpi, = ax.plot([], [], 'b-', label='Team Performance Index (TPI)')
line_ppi, = ax.plot([], [], 'r--', label='Player Performance Index (PPI)')
marker, = ax.plot([], [], 'ko', ms=6)
ax.legend()

# --- Animation functions ---
def init():
    line_tpi.set_data([], [])
    line_ppi.set_data([], [])
    marker.set_data([], [])
    return line_tpi, line_ppi, marker

def update(i):
    x = elapsed[: i + 1]
    y1 = tpi[: i + 1]
    y2 = ppi[: i + 1]
    line_tpi.set_data(x, y1)
    line_ppi.set_data(x, y2)
    if x:
        marker.set_data([x[-1]], [y1[-1]])
    return line_tpi, line_ppi, marker

# --- Run animation (fast enough) ---
ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(elapsed),
    init_func=init,
    interval=400,   # 0.4 seconds per frame
    blit=False,
    repeat=False
)

plt.show()
