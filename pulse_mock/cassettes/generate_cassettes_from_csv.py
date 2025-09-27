#!/usr/bin/env python3
"""
Generate cassette YAML files from a play-by-play CSV.

Usage:
  python generate_cassettes_from_csv.py [--csv PATH] [--outdir PATH] [--no-backup]

By default reads: pulse_mock/play_by_play_2025_jhurts.csv
and writes to: pulse_mock/cassettes/jhurts_games/

Output format matches existing cassettes: YAML with a literal JSON array
where each play JSON object is on one line and nulls are explicit.
"""
import csv
import json
import os
import argparse
import shutil
from datetime import datetime


KEY_ORDER = [
    "home_team",
    "game_seconds_remaining",
    "yards_gained",
    "passer_player_name",
    "comp_air_epa",
    "air_epa",
    "qb_epa",
    "receiver_player_name",
    "comp_yac_epa",
    "yac_epa",
    "xyac_epa",
    "wp",
    "wpa",
    "air_wpa",
    "comp_air_wpa",
    "yac_wpa",
    "comp_yac_wpa"
]


def parse_value(v):
    # Treat empty strings as None, otherwise try to convert to float, else keep string
    if v is None or v == "":
        return None
    # Try int-like -> keep float though to match .0 formatting
    try:
        f = float(v)
        return f
    except Exception:
        return v


def group_rows_by_game(csv_path):
    groups = {}
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            game_id = row.get('game_id')
            if not game_id:
                continue
            # build play dict in desired order
            play = {}
            for k in KEY_ORDER:
                # csv header names: game_seconds_remaining, home_team, yards_gained, passer_player_name, comp_air_epa, air_epa, wp, wpa, air_wpa, comp_air_wpa, qb_epa, xyac_epa
                # some keys (like comp_air_epa) match directly; we map by name
                if k in row:
                    play[k] = parse_value(row[k])
                else:
                    # fallback mapping for keys that differ (none in this CSV)
                    play[k] = None
            groups.setdefault(game_id, []).append(play)
    return groups


def make_yaml_for_game(game_id, plays, player_id='NFL_player_SyWsd7T30Oev84KlU0vKvQrU'):
    # Build the YAML string with a literal block containing a JSON array where each object is one line.
    lines = []
    lines.append('---')
    lines.append('version: 1')
    lines.append('interactions:')
    lines.append('  - request:')
    lines.append('      body: ""')
    lines.append('      form: {}')
    lines.append('      headers: {}')
    lines.append(f'      url: http://localhost:1339/v1/players/{player_id}/games/{game_id}/playbyplay')
    lines.append('      method: GET')
    lines.append('    response:')
    lines.append('      body: |')
    lines.append('        [')

    # each play as single-line JSON
    for i, p in enumerate(plays):
        # ensure keys are in KEY_ORDER
        ordered = {k: p.get(k) for k in KEY_ORDER}
        # json.dumps will produce null for None
        obj = json.dumps(ordered, ensure_ascii=False)
        comma = ',' if i < len(plays) - 1 else ''
        lines.append('          ' + obj + comma)

    lines.append('        ]')
    lines.append('      headers:')
    lines.append('        Content-Type:')
    lines.append('          - application/json')
    lines.append('      status: 200 OK')
    lines.append('      code: 200')
    return '\n'.join(lines) + '\n'


def write_cassettes(groups, outdir, backup=True):
    os.makedirs(outdir, exist_ok=True)
    written = []
    for game_id, plays in groups.items():
        filename = os.path.join(outdir, f'{game_id}.yaml')
        if backup and os.path.exists(filename):
            ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
            bak = filename + f'.bak.{ts}'
            shutil.copy2(filename, bak)
        content = make_yaml_for_game(game_id, plays)
        with open(filename, 'w', newline='') as f:
            f.write(content)
        written.append(filename)
    return written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default=os.path.join('..', 'cassettes','play_by_play_2025_jhurts.csv'), help='Path to play-by-play CSV')
    parser.add_argument('--outdir', default=os.path.join('..', 'cassettes', 'jhurts_games'), help='Output directory for yaml cassettes')
    parser.add_argument('--no-backup', dest='backup', action='store_false', help='Disable backing up existing YAML files')
    args = parser.parse_args()

    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), args.csv))
    outdir = os.path.abspath(os.path.join(os.path.dirname(__file__), args.outdir))

    if not os.path.exists(csv_path):
        print('CSV not found:', csv_path)
        return 2

    groups = group_rows_by_game(csv_path)
    written = write_cassettes(groups, outdir, backup=args.backup)
    print('Wrote', len(written), 'cassette files:')
    for p in written:
        print(' -', p)


if __name__ == '__main__':
    raise SystemExit(main())
