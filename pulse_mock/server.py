# python file: pulse_mock/PythonImpactCharts.py

import math
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter, NullFormatter
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from io import BytesIO
from flask import Flask, send_file
from flask import jsonify, make_response, Response, request
import time
import json

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import analysis
from pulse_mock.client import NFLMockClient
import numpy as np

matplotlib.use("Agg")  # headless backend

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
def get_data(player: str = None):
    client = NFLMockClient()
    ppi, tpi = analysis.compute_ppi_tpi_from_plays(client.get_game_data()[2]['plays'])
    ppi_dict = {}
    for player_entry in ppi:
        for player_name, arr in player_entry.items():
            ppi_dict[player_name] = arr
    elapsed = (3600 - tpi[:,0]).tolist()
    tpi_vals = tpi[:,1].tolist()
    # Select player PPI
    if player and player in ppi_dict:
        ppi_vals = ppi_dict[player][:,1].tolist()
    else:
        first_player = next(iter(ppi_dict)) if ppi_dict else None
        ppi_vals = ppi_dict[first_player][:,1].tolist() if first_player else [0]*len(elapsed)
    return elapsed, tpi_vals, ppi_vals

# Ensure chronological order
elapsed, tpi_vals, ppi_vals = get_data() # need to put some get request in this func call
combined = sorted(zip(elapsed, tpi_vals, ppi_vals), key=lambda x: x[0])
elapsed, tpi_vals, ppi_vals = map(list, zip(*combined))

# Axis ranges
all_y = tpi_vals + ppi_vals
ymin, ymax = min(all_y), max(all_y)
pad = (ymax - ymin) * 0.12 if ymax != ymin else 0.5

min_e, max_e = min(elapsed), max(elapsed)
start = int(math.floor(min_e / 60.0) * 60)
end = int(math.ceil(max_e / 60.0) * 60)
if start == end:
    end = start + 60

# --- Formatting helpers ---
def format_mmss(sec):
    m = int(sec) // 60
    s = int(sec) % 60
all_y = tpi_vals + ppi_vals
ymin, ymax = min(all_y), max(all_y)

app = Flask(__name__)

def render_impact_chart_bytes() -> BytesIO:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    # leave extra space at the bottom so x-axis labels don't get cropped
    ax.plot(elapsed, tpi_vals, 'b-', label='Team Performance Index (TPI)')
    ax.plot(elapsed, ppi_vals, 'r--', label='Player Performance Index (PPI)')
    if elapsed:
        ax.plot([elapsed[-1]], [tpi_vals[-1]], 'ko', ms=6)
    ax.set_xlim(start, end)
    ax.set_ylim(ymin - pad, ymax + pad)

    ax.xaxis.set_major_locator(MultipleLocator(300))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: format_mmss(int(x))))
    ax.xaxis.set_minor_locator(MultipleLocator(60))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis='x', which='major', length=7)
    ax.tick_params(axis='x', which='minor', length=3)

    ax.plot(elapsed, tpi_vals, 'b-', label='Team Performance Index (TPI)')
    ax.plot(elapsed, ppi_vals, 'r--', label='Player Performance Index (PPI)')
    if elapsed:
        ax.plot([elapsed[-1]], [tpi_vals[-1]], 'ko', ms=6)
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
        y1 = tpi_vals[: i + 1]
        y2 = ppi_vals[: i + 1]
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

@app.route('/impact_chart.json')
def impact_chart_json():
    """Return the chart data as JSON so frontends (web) can render natively.

    Adds a permissive CORS header for convenience during development.
    """
    payload = {
        'elapsed': elapsed,
        'tpi': tpi_vals,
        'ppi': ppi_vals,
        'start': start,
        'end': end,
        'ymin': ymin - pad,
        'ymax': ymax + pad
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
            payload = {'i': i, 'elapsed': elapsed[i], 'tpi': tpi_vals[i], 'ppi': ppi_vals[i]}
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


