from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import random

app = Flask(__name__)

df = pd.read_csv("play_by_play_2025.csv", low_memory=False)
hurts_df = df[df["passer"] == "J.Hurts"].copy()
hurts_df = hurts_df.dropna(subset=["qb_epa", "yards_gained", "game_seconds_remaining", "down", "ydstogo"])

hurts_df["impact_spike"] = (
    (hurts_df["qb_epa"] > 1.0) |
    (hurts_df["yards_gained"] > 15) |
    (hurts_df.get("touchdown", 0) == 1) |
    (hurts_df.get("field_goal_result", "") == "made")
).astype(int)

features = ["down", "ydstogo", "yards_gained", "qb_epa", "quarter_seconds_remaining", "game_seconds_remaining"]
hurts_df = hurts_df.dropna(subset=features)

X = hurts_df[features]
y = hurts_df["impact_spike"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)

captions_positive = [
    "Jalen Hurts is heating up... momentum spike likely incoming.", "Hurts is finding his rhythm, big play on the horizon.", "Hurts energy is shifting — watch for an impact moment soon.", "Momentum building: Hurts could change the game in the next drive."]

captions_negative = ["No big momentum shift expected right now.", "Hurts playing steady, but no major impact imminent.", "Defense holding — spike unlikely in the short term.", "Momentum steady, nothing explosive predicted."]

def generate_caption():
    sample = X.sample(1, random_state=np.random.randint(10000))
    sample_scaled = scaler.transform(sample)
    prob = model.predict_proba(sample_scaled)[0][1]
    if prob > 0.5:
        caption = random.choice(captions_positive)
    else:
        caption = random.choice(captions_negative)
    return caption, prob

@app.route("/")
def index():
    return render_template_string("""
        <html>
        <head>
            <title>Jalen Hurts Spike Predictor</title>
            <script>
                async function regenerate() {
                    let response = await fetch('/regenerate');
                    let data = await response.json();
                    document.getElementById("caption").innerText = data.caption;
                    document.getElementById("prob").innerText = "Spike likelihood: " + data.prob;
                }
            </script>
        </head>
        <body style="font-family:Arial; text-align:center; padding:20px;">
            <h2>Jalen Hurts Momentum Spike Predictor</h2>
            <p id="prob">Click below to generate prediction</p>
            <h3 id="caption">---</h3>
            <button onclick="regenerate()">Regenerate Caption</button>
        </body>
        </html>
    """)

@app.route("/regenerate")
def regenerate():
    caption, prob = generate_caption()
    return jsonify({"caption": caption, "prob": f"{prob:.2f}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

 