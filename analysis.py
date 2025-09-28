import numpy as np
import pandas as pd

def compute_ppi_tpi_from_plays(plays_json):
    """
    Compute real-time Player Performance Index (PPI) and 
    Team Performance Index (TPI) arrays from cassette play-by-play data.
    
    Parameters:
        plays_json (list of dicts): JSON list of plays from cassette
    
    Returns:
        ppi_array, tpi_array (numpy arrays with shape [n,2])
        Each row = [timestamp, value]
    """

    df = pd.DataFrame(plays_json)

    # clean data
    df = df.fillna(0)
    df['passer_player_name'] = df['passer_player_name'].fillna("Unknown")
    df['receiver_player_name'] = df['receiver_player_name'].fillna("Unknown")
    df = df.drop_duplicates(subset=['game_seconds_remaining'], keep='first').reset_index(drop=True)

    # calculate PPI at instant of event based on a position & its formula
    def calc_ppi(timestamp, position: str):
        if position == "QB":
            return 0.5 * df["qb_epa"] + 0.2 * df["air_epa"] + 0.2 * df["wpa"] + 0.1 * (df["yards_gained"] / 10)
        elif position == "WR":
            return 0.4 * df["yac_epa"] + 0.3 * df["air_epa"] + 0.2 * df["wpa"] + 0.1 * (df["yards_gained"] / 10)
        else:
            return 0.4 * df["epa"] + 0.3 * df["wpa"] + 0.2 * df["success"]
        # add more position formulas if time allows

    # given a player name, compute their PPI time series
    def get_player_ppi_time_series(player_name: str, position: str):
        """
        Compute PPI time series for one player.
        player_name: str
        Returns: {player_name: np.array([[timestamp, ppi], ...])}
        """

        data = []
        for _, row in events.iterrows():
            timestamp = row["game_seconds_remaining"]
            values = [row.get(m, 0.0) for m in metrics]
            ppi_val = calc_ppi(timestamp, position) # create weighted formula if time allows
            data.append([timestamp, ppi_val])

        return {player_name: np.array(data)}
    

    # Step 2: Define PPI scoring
    def compute_player_ppi(row):
        w_epa, w_wpa, w_air, w_yac, w_success = 0.4, 0.3, 0.1, 0.1, 0.1
        x = (row["epa"] * w_epa +
            row["wpa"] * w_wpa +
            row["air_epa"] * w_air +
            row["yac_epa"] * w_yac +
            row["success"] * w_success)
        print(x)
        return (
            row["epa"] * w_epa +
            row["wpa"] * w_wpa +
            row["air_epa"] * w_air +
            row["yac_epa"] * w_yac +
            row["success"] * w_success
        )

    # Step 3: Real-time calculations
    ppi_over_time, tpi_over_time = [], []

    for ts in sorted(df["timestamp"].unique()):
        plays_at_ts = df[df["timestamp"] == ts]

        # Player PPI (mean of per-play PPI for each player at this timestamp)
        ppi_per_player = plays_at_ts.groupby("player_id", group_keys=False).apply(lambda d: d.apply(compute_player_ppi, axis=1), include_groups=False)
        print(ppi_per_player)
        avg_ppi = ppi_per_player.mean()
        # If avg_ppi is a Series, extract scalar
        if isinstance(avg_ppi, pd.Series):
            avg_ppi = avg_ppi.item() if avg_ppi.size == 1 else avg_ppi.mean()
        ppi_over_time.append([ts, float(avg_ppi) if not pd.isnull(avg_ppi) else 0.0])

        # Team TPI (sum of per-play PPI for all players in each team at this timestamp)
        tpi_per_team = plays_at_ts.groupby("team_id", group_keys=False).apply(
            lambda d: d.groupby("player_id", group_keys=False).apply(lambda x: x.apply(compute_player_ppi, axis=1), include_groups=False).sum(),
            include_groups=False
        )

        avg_tpi = tpi_per_team.mean()
        if isinstance(avg_tpi, pd.Series):
            avg_tpi = avg_tpi.item() if avg_tpi.size == 1 else avg_tpi.mean()
        tpi_over_time.append([ts, float(avg_tpi) if not pd.isnull(avg_tpi) else 0.0])

    # Step 4: Output as numpy arrays
    return np.array(ppi_over_time), np.array(tpi_over_time)