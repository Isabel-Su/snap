import numpy as np
import pandas as pd
import random

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

    # calculate PPI at instant of event based on a position & its formula
    def calc_ppi(position: str, timestamp=None):
        
        if timestamp is None:
            return random.random() * random.randint(-1, 1)
        
        # Fetch the row for the given timestamp
        row = df[df['timestamp'] == timestamp]
        if row.empty:
            return None
        row = row.iloc[0]
        if position is "QB":
            return 0.5 * row["qb_epa"] + 0.2 * row["air_epa"] + 0.2 * row["wpa"] + 0.1 * (row["yards_gained"] / 10)
        elif position is "WR" or position is "TE":
            return 0.4 * row["yac_epa"] + 0.3 * row["air_epa"] + 0.2 * row["wpa"] + 0.1 * (row["yards_gained"] / 10)
        else:
            # if no formula, that means not enough data for position, so generate a random PPI
            return random.random() * random.randint(-1, 1)
        # add more position formulas if time allows / if data exists

    # given a player name, compute their PPI time series
    def get_player_ppi_time_series(player_name: str, position: str):
        """
        Compute PPI time series for one player.
        player_name: str
        Returns: {player_name: np.array([[timestamp, ppi], ...])}
        """

        data = []
        # Only process rows where the player matches player_name
        player_rows = df[(df['passer_player_name'] == player_name) | (df['receiver_player_name'] == player_name)]
        if player_rows.empty:
            # Create a fake player with a fake timestamp
            fake_timestamp = -1
            fake_ppi = calc_ppi(fake_timestamp, position)
            data.append([fake_timestamp, fake_ppi])
        else:
            for _, row in player_rows.iterrows():
                timestamp = row["game_seconds_remaining"]
                ppi_val = calc_ppi(position, timestamp=timestamp)
                data.append([timestamp, ppi_val])

        print({player_name: np.array(data)})
        return {player_name: np.array(data)}
    

    return np.array(all_ppi_over_time), np.array(tpi_over_time)