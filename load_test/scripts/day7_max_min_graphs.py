# -*- coding: utf-8 -*-
"""
Day 7 - API별 Max/Min Latency 그래프
실행: python load_test/scripts/day7_max_min_graphs.py
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ===========================
# 경로 설정
# ===========================
BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "processed" / "unified_summary.csv"

# ===========================
# 한글 폰트 설정 (Windows)
# ===========================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ===========================
# 데이터 로드
# ===========================
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
df = df[df["api"] != "TOTAL"].copy()

USERS = [10, 30, 50, 70, 100]
APIS = ["Auth", "과목 정보", "시험 입장", "시험 시작", "시험 제출", "재응시"]
COLORS = {"team2": "#4C72B0", "team3": "#DD8452"}
MARKERS = {"team2": "o", "team3": "s"}
Y_MAX = 800


# ===========================
# 그래프 1 — Max Latency 추이
# ===========================
n_cols = 3
n_rows = (len(APIS) + n_cols - 1) // n_cols

fig1, axes1 = plt.subplots(n_rows, n_cols, figsize=(18, n_rows * 5))
fig1.suptitle("유저 증가에 따른 API별 Max Latency 변화 (2팀 vs 3팀)",
              fontsize=15, fontweight='bold')
axes1_flat = axes1.flatten()

for idx, api in enumerate(APIS):
    ax = axes1_flat[idx]
    for team in ["team2", "team3"]:
        data = df[(df["api"] == api) & (df["team"] == team)].sort_values("users")
        if not data.empty:
            ax.plot(data["users"], data["max_latency_ms"],
                    marker=MARKERS[team], color=COLORS[team],
                    label=team, linewidth=2, markersize=7)
            for _, row in data.iterrows():
                ax.annotate(f"{int(row['max_latency_ms'])}",
                           xy=(row['users'], row['max_latency_ms']),
                           xytext=(0, 6), textcoords='offset points',
                           ha='center', fontsize=7, color=COLORS[team])

    ax.set_ylim(0, Y_MAX)
    ax.set_title(api, fontweight='bold', fontsize=11)
    ax.set_xlabel("동시 사용자 수 (명)")
    ax.set_ylabel("Max 응답시간 (ms)")
    ax.set_xticks(USERS)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

for idx in range(len(APIS), len(axes1_flat)):
    axes1_flat[idx].set_visible(False)

plt.tight_layout()
out1 = BASE_DIR / "processed" / "day7_max_latency_by_api.png"
plt.savefig(out1, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 저장 완료: {out1}")


# ===========================
# 그래프 2 — Min Latency 추이
# ===========================
fig2, axes2 = plt.subplots(n_rows, n_cols, figsize=(18, n_rows * 5))
fig2.suptitle("유저 증가에 따른 API별 Min Latency 변화 (2팀 vs 3팀)",
              fontsize=15, fontweight='bold')
axes2_flat = axes2.flatten()

for idx, api in enumerate(APIS):
    ax = axes2_flat[idx]
    for team in ["team2", "team3"]:
        data = df[(df["api"] == api) & (df["team"] == team)].sort_values("users")
        if not data.empty:
            ax.plot(data["users"], data["min_latency_ms"],
                    marker=MARKERS[team], color=COLORS[team],
                    label=team, linewidth=2, markersize=7)
            for _, row in data.iterrows():
                ax.annotate(f"{int(row['min_latency_ms'])}",
                           xy=(row['users'], row['min_latency_ms']),
                           xytext=(0, 6), textcoords='offset points',
                           ha='center', fontsize=7, color=COLORS[team])

    ax.set_ylim(0, 500)
    ax.set_title(api, fontweight='bold', fontsize=11)
    ax.set_xlabel("동시 사용자 수 (명)")
    ax.set_ylabel("Min 응답시간 (ms)")
    ax.set_xticks(USERS)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

for idx in range(len(APIS), len(axes2_flat)):
    axes2_flat[idx].set_visible(False)

plt.tight_layout()
out2 = BASE_DIR / "processed" / "day7_min_latency_by_api.png"
plt.savefig(out2, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 저장 완료: {out2}")