import json
import os

SCORE_FILE = "scores.json"

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE, "r") as file:
        return json.load(file)

def save_score(name, level, score, wpm, accuracy):
    scores = load_scores()
    scores.append({
        "name": name,
        "level": level,
        "score": score,
        "wpm": round(wpm, 2),
        "accuracy": round(accuracy, 2)
    })

    # Urutkan dari nilai skor tertinggi
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)

    with open(SCORE_FILE, "w") as file:
        json.dump(scores, file, indent=4)

def show_top_scores(level):
    print(f"\n=== Leaderboard Level {level} ===")
    scores = load_scores()
    filtered = [s for s in scores if s['level'] == level]

    if not filtered:
        print("Belum ada skor untuk level ini.")
        return

    # Ambil 5 terbaik
    filtered = filtered[:5]
    for i, s in enumerate(filtered, start=1):
        print(f"{i}. {s['name']} — Score: {s['score']} | WPM: {s['wpm']} | Acc: {s['accuracy']}%")
