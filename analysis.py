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
        ppi_over_time (list of dicts with player name as key and np.arrays with shape [n,2] as value)
        tpi_over_time (np.array with shape [n,2])
        Each row = [timestamp, performance index]
    """

    df = pd.DataFrame(plays_json)

    # clean data
    df = df.fillna(0)
    df['passer_player_name'] = df['passer_player_name'].fillna("Unknown")
    df['receiver_player_name'] = df['receiver_player_name'].fillna("Unknown")

    # calculate PPI at instant of event based on a position & its formula
    def calc_ppi(position: str, timestamp):
        """
        Calculate the Player Performance Index (PPI) for a given position and timestamp.
        Parameters:
            position (str): The position of the player (e.g., 'QB', 'WR', 'TE', etc.)
            timestamp: The timestamp to fetch the play from the DataFrame.
        Returns:
            float: The calculated PPI value for the player at the given timestamp, or a random value if not enough data.
        """
        
        # Fetch the row for the given timestamp
        row = df[df['game_seconds_remaining'] == timestamp]

        # go here if timestamp passed in is -1 (fake player)
        if row.empty:
            # not enough info to generate a random ppi for this position
            # create a random PPI between -1 and 1
            return random.random() * 2 - 1
        row = row.iloc[0]

        # player is a passer
        if position == "QB":
            return 0.5 * row["qb_epa"] + 0.2 * row["air_epa"] + 0.2 * row["wpa"] + 0.1 * (row["yards_gained"] / 10)
        # player == a receiver
        elif position == "WR" or position == "TE":
            return 0.4 * row["yac_epa"] + 0.3 * row["air_epa"] + 0.2 * row["wpa"] + 0.1 * (row["yards_gained"] / 10)
        else:
            return random.random() * random.randint(-1, 1) # something went wrong
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
        
        # if player is fake due to lack of data
        if player_rows.empty:
            # Create a fake player with a fake timestamp
            for i in range(random.randrange(5, 15)):
                # generate fake timestamps at random intervals, with each interval between 60 and 500 seconds
                fake_timestamp = i * random.random() * 440 + 60
                fake_ppi = calc_ppi(position, -1)
                data.append([fake_timestamp, fake_ppi])

        # player is real
        else:
            for _, row in player_rows.iterrows():
                timestamp = row["game_seconds_remaining"]
                ppi_val = calc_ppi(position, timestamp=timestamp)
                data.append([timestamp, ppi_val])

        # print({player_name: np.array(data)})
        return {player_name: np.array(data)}
    
    # create fake players with fake PPI time series, default values based on typical NFL roster sizes
    # returns a dict of fake players with fake PPI time series
    def create_fake_players_ppi_time_series(num_qb=3, num_rb=4, num_wr=5, num_te=4, num_c=2, num_g=2, num_ot=5, num_de=2, num_dt=5, num_lb=8, num_cb=6, num_s=4, num_pk=1, num_p=1, num_ls=1):
        """
        Creates all necessary fake players with fake PPI time series.
        Returns: list of {player_name: np.array([[timestamp, ppi], ...])}
        """
        players_ppi = []
        position_counts = {
            "QB": num_qb,
            "RB": num_rb,
            "WR": num_wr,
            "TE": num_te,
            "C": num_c,
            "G": num_g,
            "OT": num_ot,
            "DE": num_de,
            "DT": num_dt,
            "LB": num_lb,
            "CB": num_cb,
            "S": num_s,
            "PK": num_pk,
            "P": num_p,
            "LS": num_ls
        }
        for pos, count in position_counts.items():
            for i in range(count):
                player_name = f"Fake_{pos}_{i+1}"
                players_ppi.append(get_player_ppi_time_series(player_name, pos))
        # Sort each player's time series in decreasing order by timestamp
        sorted_players_ppi = []
        for player_dict in players_ppi:
            for player_name, arr in player_dict.items():
                # Sort by timestamp descending
                arr_sorted = np.array(sorted(arr, key=lambda x: x[0], reverse=True))
                sorted_players_ppi.append({player_name: arr_sorted})
        return sorted_players_ppi
    
    def aggregate_real_players_ppi_time_series():
        """
        Aggregate PPI time series for all real players in the DataFrame.
        Returns: list of {player_name: np.array([[timestamp, ppi], ...])}
        """
        players_ppi = []
        # Get all unique passers and receivers in the DataFrame
        real_player_names = set(df['passer_player_name'].unique()).union(set(df['receiver_player_name'].unique()))
        for real_player in real_player_names:
            # Infer position for real players
            if real_player in df['passer_player_name'].values:
                position = "QB"
            elif real_player in df['receiver_player_name'].values:
                position = "WR"  # Could be "TE" if more data available
            else:
                position = "Unknown" # something went wrong
            players_ppi.append(get_player_ppi_time_series(real_player, position))
        return players_ppi
    
    all_ppi_over_time = (aggregate_real_players_ppi_time_series() + create_fake_players_ppi_time_series(num_qb=2, num_wr=0))[1:]
    # print(all_ppi_over_time)


    def get_team_tpi_time_series():
        """
        Compute TPI time series for one team passed into compute_ppi_tpi_from_plays.
        Returns: np.array([[timestamp, tpi], ...])
        """

        data = []
        # Get all unique timestamps
        timestamps = sorted(df['game_seconds_remaining'].unique())
        # For each timestamp, sum PPI for all team players
        for ts in timestamps:
            tpi_val = 0.0
            for player_ppi_dict in all_ppi_over_time:
                for _, player_ppi_arr in player_ppi_dict.items():
                    ppi_at_ts = player_ppi_arr[player_ppi_arr[:,0] == ts, 1]
                    if ppi_at_ts.size > 0:
                        tpi_val += ppi_at_ts[0]
            data.append([ts, tpi_val])
        # print("TPI time series data:", np.array)
        return np.array(data)
    
    return all_ppi_over_time, get_team_tpi_time_series()