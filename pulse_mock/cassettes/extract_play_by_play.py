import pandas as pd

df = pd.read_csv("pulse_mock/cassettes/play_by_play_2025.csv")
cols = [
	"game_id",
	"home_team",
	"game_seconds_remaining",
	"yards_gained",
	"passer_player_name",
	"comp_air_epa",
	"air_epa",
	"wp",
	"wpa",
	"air_wpa",
	"comp_air_wpa",
	"qb_epa",
	"xyac_epa"
]
df[cols].to_csv("pulse_mock/cassettes/play_by_play_2025_filtered.csv", index=False)
print("Saved to pulse_mock/cassettes/play_by_play_2025_filtered.csv")
