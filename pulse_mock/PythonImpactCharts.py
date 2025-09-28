# python file: pulse_mock/PythonImpactCharts.py

import math
import matplotlib
matplotlib.use("Agg")              # headless backend
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter, NullFormatter
from io import BytesIO
import math
import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter, NullFormatter
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from io import BytesIO
from flask import Flask, send_file
import os
import tempfile
from flask import jsonify, make_response, Response, request
import threading
import time
import json

plt.style.use("fivethirtyeight")
# Attempt to register the user's local "Industry" font files so matplotlib
# text uses the same typography. This is defensive: if the font files are
# not present the code will quietly fall back to Matplotlib's defaults.
try:
    import matplotlib.font_manager as fm
    _candidate_paths = [
        '/Users/riasharma/Downloads/Industry Test/IndustryDemi-Regular.otf',
        '/Users/riasharma/Downloads/Industry Test/IndustryDemi-Bold.otf',
        '/Users/riasharma/Downloads/Industry Test/Industry-Medi.otf',
    ]
    _added = False
    for _p in _candidate_paths:
        if os.path.exists(_p):
            try:
                fm.fontManager.addfont(_p)
                _added = True
            except Exception:
                # non-fatal if addfont fails for any file
                pass
    if _added:
        # Prefer the Industry family for sans-serif text; include common
        # fallbacks so labels still render if exact names differ.
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = [
            'Industry Medi',
            'IndustryDemi',
            'IndustryDemi-Bold',
            'DejaVu Sans',
        ]
except Exception:
    # Don't let font registration prevent the module from importing.
    pass

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

app = Flask(__name__)


def render_impact_chart_bytes() -> BytesIO:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    # leave extra space at the bottom so x-axis labels don't get cropped
    fig.subplots_adjust(bottom=0.22)
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

    ax.plot(elapsed, tpi, 'b-', label='Team Performance Index (TPI)')
    ax.plot(elapsed, ppi, 'r--', label='Player Performance Index (PPI)')
    if elapsed:
        ax.plot([elapsed[-1]], [tpi[-1]], 'ko', ms=6)
    ax.legend()

    buf = BytesIO()
    # save without tight bbox; we've already made room via subplots_adjust
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


@app.route('/impact_chart')
def impact_chart():
    buf = render_impact_chart_bytes()
    return send_file(buf, mimetype='image/png', as_attachment=False, download_name='impact_chart.png')


# --- Animated GIF endpoint (cached) ---
_gif_lock = threading.Lock()
_gif_cache_path = os.path.join(os.path.dirname(__file__), 'impact_chart.gif')

def generate_impact_gif(path: str, interval_ms: int = 300):
    """Generate an animated GIF at `path`. Overwrites existing file."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    # ensure bottom margin so x-axis labels are visible in GIF frames
    fig.subplots_adjust(bottom=0.22)
    ax.set_title("Microeconomy Impact Chart")
    ax.set_xlabel("Game Time (MM:SS elapsed)")
    ax.set_ylabel("Performance Index")
    ax.set_xlim(start, end)
    ax.set_ylim(ymin - pad, ymax + pad)

    ax.xaxis.set_major_locator(MultipleLocator(300))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: format_mmss(int(x))))
    ax.xaxis.set_minor_locator(MultipleLocator(60))
    ax.xaxis.set_minor_formatter(NullFormatter())
    plt.setp(ax.get_xticklabels(), rotation=45)
    ax.grid(alpha=0.3)

    line_tpi, = ax.plot([], [], 'b-', label='Team Performance Index (TPI)')
    line_ppi, = ax.plot([], [], 'r--', label='Player Performance Index (PPI)')
    marker, = ax.plot([], [], 'ko', ms=6)
    ax.legend()

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

    frames = len(elapsed)
    ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init, interval=interval_ms, blit=False, repeat=False)

    # fps for PillowWriter: frames per second
    fps = max(1, int(1000 / interval_ms))
    writer = PillowWriter(fps=fps)
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ani.save(path, writer=writer)
    plt.close(fig)


@app.route('/impact_chart.gif')
def impact_chart_gif():
    """Return a cached animated GIF; generate it on first request."""
    # If cache exists, return it
    if os.path.exists(_gif_cache_path):
        return send_file(_gif_cache_path, mimetype='image/gif')

    # Prevent concurrent generation
    with _gif_lock:
        # Double-check after acquiring lock
        if os.path.exists(_gif_cache_path):
            return send_file(_gif_cache_path, mimetype='image/gif')

        # Generate GIF (may take a moment)
        try:
            # Use temporary file then atomically rename
            fd, tmp_path = tempfile.mkstemp(suffix='.gif', dir=os.path.dirname(_gif_cache_path))
            os.close(fd)
            generate_impact_gif(tmp_path, interval_ms=300)
            os.replace(tmp_path, _gif_cache_path)
            return send_file(_gif_cache_path, mimetype='image/gif')
        except Exception:
            # cleanup tmp if exists
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass
            raise


@app.route('/impact_chart.json')
def impact_chart_json():
    """Return the chart data as JSON so frontends (web) can render natively.

    Adds a permissive CORS header for convenience during development.
    """
    payload = {
        'elapsed': elapsed,
        'tpi': tpi,
        'ppi': ppi,
        'start': start,
        'end': end,
        'ymin': ymin - pad,
        'ymax': ymax + pad,
    }
    resp = make_response(jsonify(payload))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/impact_chart/stream')
def impact_chart_stream():
    """Server-Sent Events endpoint that streams chart points one at a time.

    Query params:
      interval_ms=<int>  -> how many milliseconds to wait between points (default 500)
    """
    interval_raw = request.args.get('interval_ms', '500')
    try:
        interval_ms = int(interval_raw)
    except Exception:
        interval_ms = 500
    interval_ms = max(50, min(20000, interval_ms))

    def generate():
        for i in range(len(elapsed)):
            payload = {'i': i, 'elapsed': elapsed[i], 'tpi': tpi[i], 'ppi': ppi[i]}
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(interval_ms / 1000.0)
        # final event to indicate completion
        yield "event: done\ndata: {}\n\n"

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'text/event-stream',
        'Access-Control-Allow-Origin': '*',
    }
    return Response(generate(), headers=headers)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)