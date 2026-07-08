'''
Qualifying Top Speed Championship Analysis

Find (across any year) which team would win the championship if results were only
based on top speed (from qualifying)

Author: Jazib Ahmed
'''
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from fastf1.plotting import get_team_color
import fastf1.plotting as f1plot


# -----------------------------
# SETTINGS
# -----------------------------
year = 2025
figsize = (12, 8)  # consistent size for all figures

plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = '#2b2b2b'
plt.rcParams['axes.facecolor'] = '#2b2b2b'
plt.rcParams['savefig.facecolor'] = '#2b2b2b'

fastf1.Cache.enable_cache('fastf1_cache')

f1_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

# Get calendar
calendar = fastf1.get_event_schedule(year, include_testing=False)

races = list(calendar['EventName'])

# -----------------------------
# STORAGE
# -----------------------------
race_team_speeds = {}

team_points = defaultdict(int)
team_history = defaultdict(list)

round_winners = []  # {"Round": "R1", "Team": ..., "Speed": ...}

# -----------------------------
# PROCESS EACH QUALIFYING SESSION
# -----------------------------
for round_num, race in enumerate(races, start=1):

    print(f"Loading {race} Qualifying...")

    try:
        #Load each qualifying
        session = fastf1.get_session(year, race, 'Q')
        session.load(telemetry=False, weather=False, messages=False)

        laps = session.laps

        team_speeds = {}

        for team in laps['Team'].dropna().unique():
            team_laps = laps.pick_teams(team)
            max_speed = team_laps['SpeedST'].max()

            if pd.notna(max_speed):
                team_speeds[team] = max_speed

        race_team_speeds[race] = team_speeds

        ranked_teams = sorted( team_speeds.items(), key=lambda x: x[1],
            reverse=True)

        # Capturing race winner (team)
        if ranked_teams:
            winner_team, winner_speed = ranked_teams[0]
            round_winners.append({
                "Round": f"R{round_num}",
                "Team": winner_team,
                "Speed": winner_speed
            })

        # Add team's points based on points system from f1_points variable
        for pos, (team, speed) in enumerate(ranked_teams[:10]):
            points = f1_points[pos]
            team_points[team] += points

        # Keeping track of points gained each race
        all_teams = set(team_history.keys()) | set(team_points.keys())
        for team in all_teams:
            team_history[team].append(team_points[team])

    except Exception as e:
        print(f"Skipped {race}: {e}")


# =====================================================
# TABLE 1: TOP 10 STANDINGS
# =====================================================

# Getting the final points results
final_standings = sorted(team_points.items(), key=lambda x: x[1],
    reverse=True)[:10]
table1_data = [[team, str(points)] for team, points in final_standings]

# Plot settings
fig1, ax1 = plt.subplots(figsize=figsize)
ax1.axis('off')

tbl1 = ax1.table(
    cellText=table1_data,
    colLabels=["Team", "Points"],
    loc='center',
    cellLoc='center',
    colLoc='center'
)

tbl1.set_fontsize(16)
tbl1.scale(1, 2.7)

# Style header row
for col in range(2):
    cell = tbl1[0, col]
    cell.set_facecolor("#454545")
    cell.set_text_props(color="white", fontweight="bold")
    cell.set_edgecolor("#8a8a8a")

# Alternate row shading + team color accents
for row_idx, (team, points) in enumerate(final_standings, start=1):
    try:
        color = get_team_color(team, session=session)
    except Exception:
        color = "#aaaaaa"

    bg = "#3a3a3a" if row_idx % 2 == 0 else "#2b2b2b"

    for col in range(2):
        cell = tbl1[row_idx, col]
        cell.set_facecolor(bg)
        cell.set_edgecolor("#707070")
        cell.set_text_props(color="white")

    tbl1[row_idx, 0].set_text_props(color=color, fontweight="bold")

# Title name
ax1.set_title(
    f"{year} Qualifying Top Speed Championship Final Standings",
    fontsize=20, pad=20, fontweight="bold", color="white"
)
plt.tight_layout()
plt.show()


# =====================================================
# TABLE 2: ROUND WINNERS, 2 COLUMNS x 12 ROWS
# =====================================================

# Finding number of races so table can be split them into 2 columns
n = len(round_winners)
half = (n + 1) // 2

left_half = round_winners[:half]
right_half = round_winners[half:]

while len(right_half) < len(left_half):
    right_half.append({"Round": "", "Team": "", "Speed": None})

table2_data = []
for left, right in zip(left_half, right_half):
    left_speed = f"{left['Speed']:.1f}" if pd.notna(left.get("Speed")) else ""
    right_speed = f"{right['Speed']:.1f}" if pd.notna(right.get("Speed")) else ""
    table2_data.append([
        left["Round"], left["Team"], left_speed,
        right["Round"], right["Team"], right_speed
    ])

col_labels = ["Round", "Winner", "Top Speed (km/h)", "Round", "Winner", "Top Speed (km/h)"]

# Plot settings
fig2, ax2 = plt.subplots(figsize=figsize)
ax2.axis('off')

tbl2 = ax2.table(
    cellText=table2_data,
    colLabels=col_labels,
    loc='center',
    cellLoc='center',
    colLoc='center'
)

tbl2.auto_set_font_size(False)
tbl2.set_fontsize(14)
tbl2.scale(1, 2.3)

# Style header row
for col in range(6):
    cell = tbl2[0, col]
    cell.set_facecolor("#454545")
    cell.set_text_props(color="white", fontweight="bold")
    cell.set_edgecolor("#8a8a8a")

# Alternate row shading + team color accents for both winner columns
for row_idx in range(1, len(table2_data) + 1):
    bg = "#3a3a3a" if row_idx % 2 == 0 else "#2b2b2b"
    for col in range(6):
        cell = tbl2[row_idx, col]
        cell.set_facecolor(bg)
        cell.set_edgecolor("#707070")
        cell.set_text_props(color="white")

    left_team = table2_data[row_idx - 1][1]
    right_team = table2_data[row_idx - 1][4]

    if left_team:
        try:
            color = get_team_color(left_team, session=session)
        except Exception:
            color = "#aaaaaa"
        tbl2[row_idx, 1].set_text_props(color=color, fontweight="bold")

    if right_team:
        try:
            color = get_team_color(right_team, session=session)
        except Exception:
            color = "#aaaaaa"
        tbl2[row_idx, 4].set_text_props(color=color, fontweight="bold")

ax2.set_title(
    f"{year} Qualifying Top Speed Round Winners",
    fontsize=20, pad=20, fontweight="bold", color="white"
)
plt.tight_layout()
plt.show()


# -----------------------------
# PLOT CHAMPIONSHIP PROGRESSION
# -----------------------------
fig3, ax3 = plt.subplots(figsize=figsize)

for team, history in team_history.items():
    try:
        color = get_team_color(team, session=session)
    except Exception:
        color = "white"

    ax3.plot(
        range(1, len(history) + 1),
        history,
        marker='o',
        color=color,
        linewidth=2,
        label=team
    )

ax3.set_title(f"{year} Qualifying Top Speed Championship", fontsize=20, color="white", fontweight="bold")
ax3.set_ylabel("Championship Points", fontsize=12, color="white")

ax3.set_xticks(range(1, len(races) + 1))
ax3.set_xticklabels(races, rotation=45, ha='right', color="white")
ax3.tick_params(colors="white")

ax3.grid(True, alpha=0.2, color="gray")
ax3.legend(facecolor="#1a1a1a", edgecolor="#444444", labelcolor="white")

plt.tight_layout()
plt.show()