# -*- coding: utf-8 -*-
"""
Day 7 - 유저 증가에 따른 API별 평균 응답시간 그래프
실행: python load_test/scripts/day7_avg_latency_graph.py
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ===========================
# 경로 설정
# ===========================
BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "processed" / "unified_summary.csv"
OUTPUT_PATH = BASE_DIR / "processed" / "day7_avg_latency_graph.png"

# ===========================
# 한글 폰트 설정 (Windows)
# ===========================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ===========================
# 데이터 로드
# ===========================
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

# TOTAL 제외
df = df[df["api"] != "TOTAL"].copy()

# 유저 단계
USERS = [10, 30, 50, 70, 100]
APIS = df["api"].unique().tolist()
TEAMS = ["team2", "team3"]
COLORS = {"team2": "#4C72B0", "team3": "#DD8452"}
MARKERS = {"team2": "o", "team3": "s"}
Y_MAX = 600

# ===========================
# 그래프 1 — API별 팀 비교 (서브플롯)
# ===========================
n_apis = len(APIS)
n_cols = 3
n_rows = (n_apis + n_cols - 1) // n_cols
fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, n_rows * 5))
fig.suptitle("유저 증가에 따른 API별 평균 응답시간 변화 (2팀 vs 3팀)",
             fontsize=15, fontweight='bold')

axes_flat = axes.flatten()

for idx, api in enumerate(APIS):
    ax = axes_flat[idx]
    for team in TEAMS:
        team_data = df[(df["api"] == api) & (df["team"] == team)].sort_values("users")
        if not team_data.empty:
            ax.plot(
                team_data["users"],
                team_data["avg_latency_ms"],
                marker=MARKERS[team],
                color=COLORS[team],
                label=team,
                linewidth=2,
                markersize=7,
            )
    ax.axhline(y=1000, color='red', linestyle='--', alpha=0.6, linewidth=1, label='기준 (1000ms)')
    ax.set_ylim(0, Y_MAX)
    ax.set_title(api, fontweight='bold', fontsize=11)
    ax.set_xlabel("동시 사용자 수 (명)")
    ax.set_ylabel("평균 응답시간 (ms)")
    ax.set_xticks(USERS)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

# 빈 subplot 숨기기
for idx in range(len(APIS), len(axes_flat)):
    axes_flat[idx].set_visible(False)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 그래프 저장 완료: {OUTPUT_PATH}")

# ===========================
# 그래프 2 — 전체 API 통합 비교
# ===========================
OUTPUT_PATH2 = BASE_DIR / "processed" / "day7_avg_latency_total.png"

fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle("유저 증가에 따른 전체 평균 응답시간 추이",
              fontsize=14, fontweight='bold')

for i, team in enumerate(TEAMS):
    ax = axes2[i]
    team_data = df[df["team"] == team]
    for api in APIS:
        api_data = team_data[team_data["api"] == api].sort_values("users")
        if not api_data.empty:
            ax.plot(
                api_data["users"],
                api_data["avg_latency_ms"],
                marker='o',
                label=api,
                linewidth=2,
                markersize=6,
            )
    ax.axhline(y=1000, color='red', linestyle='--', alpha=0.6, linewidth=1.5, label='기준 (1000ms)')
    ax.set_ylim(0, Y_MAX)
    ax.set_title(f"{team} - API별 평균 응답시간", fontweight='bold')
    ax.set_xlabel("동시 사용자 수 (명)")
    ax.set_ylabel("평균 응답시간 (ms)")
    ax.set_xticks(USERS)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_PATH2, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 그래프 저장 완료: {OUTPUT_PATH2}")

# ===========================
# 수치 요약 출력
# ===========================
print("\n=== API별 평균 응답시간 요약 (ms) ===")
pivot = df.pivot_table(
    index=["team", "api"],
    columns="users",
    values="avg_latency_ms",
    aggfunc="mean"
)
print(pivot.to_string())

print("\n=== 병목 구간 식별 (평균 응답시간 상위 3개) ===")
top3 = df[df["users"] == 100].nlargest(3, "avg_latency_ms")[["team", "api", "avg_latency_ms", "max_latency_ms"]]
print(top3.to_string(index=False))