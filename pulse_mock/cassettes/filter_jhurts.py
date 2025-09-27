import pandas as pd

df = pd.read_csv("pulse_mock/cassettes/play_by_play_2025_filtered.csv")
filtered = df[df["passer_player_name"].fillna('').str.lower().str.contains("j.hurts")]
filtered.to_csv("pulse_mock/cassettes/play_by_play_2025_jhurts.csv", index=False)
print("Saved to pulse_mock/cassettes/play_by_play_2025_jhurts.csv")
