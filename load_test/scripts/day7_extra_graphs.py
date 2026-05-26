# -*- coding: utf-8 -*-
"""
Day 7 - 추가 시각화
1. 히트맵 - 팀별 API × 유저 수 응답시간
2. 막대그래프 - 100명 기준 2팀 vs 3팀 API별 비교
실행: python load_test/scripts/day7_extra_graphs.py
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
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


# ===========================
# 그래프 1 — 히트맵
# ===========================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("API × 유저 수별 평균 응답시간 히트맵 (ms)", fontsize=14, fontweight='bold')

for i, team in enumerate(["team2", "team3"]):
    ax = axes[i]
    team_data = df[df["team"] == team]

    # pivot table 생성
    pivot = team_data.pivot_table(
        index="api",
        columns="users",
        values="avg_latency_ms",
        aggfunc="mean"
    )
    # API 순서 정렬
    pivot = pivot.reindex([a for a in APIS if a in pivot.index])
    pivot = pivot.reindex(columns=USERS)

    im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    plt.colorbar(im, ax=ax, label="응답시간 (ms)")

    # 축 설정
    ax.set_xticks(range(len(USERS)))
    ax.set_xticklabels([f"{u}명" for u in USERS])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title(f"{team}", fontweight='bold', fontsize=12)

    # 셀 값 표시
    for row_idx in range(len(pivot.index)):
        for col_idx in range(len(USERS)):
            val = pivot.values[row_idx, col_idx]
            if not np.isnan(val):
                ax.text(col_idx, row_idx, f"{int(val)}",
                       ha='center', va='center', fontsize=9,
                       color='black' if val < 300 else 'white', fontweight='bold')

plt.tight_layout()
output1 = BASE_DIR / "processed" / "day7_heatmap.png"
plt.savefig(output1, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 히트맵 저장 완료: {output1}")


# ===========================
# 그래프 2 — 100명 기준 막대그래프
# ===========================
fig2, ax2 = plt.subplots(figsize=(14, 6))

df_100 = df[df["users"] == 100]
x = np.arange(len(APIS))
width = 0.35
colors = {"team2": "#4C72B0", "team3": "#DD8452"}

for i, team in enumerate(["team2", "team3"]):
    team_data = df_100[df_100["team"] == team].set_index("api")
    vals = [team_data.loc[api, "avg_latency_ms"] if api in team_data.index else 0 for api in APIS]
    bars = ax2.bar(x + i * width, vals, width, label=team,
                   color=colors[team], alpha=0.85, edgecolor='white')

    # 막대 위에 값 표시
    for bar, val in zip(bars, vals):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                    f"{int(val)}ms", ha='center', va='bottom', fontsize=9, fontweight='bold')

ax2.axhline(y=1000, color='red', linestyle='--', alpha=0.7, linewidth=1.5, label='기준값 (1000ms)')
ax2.set_title("100명 기준 API별 평균 응답시간 비교 (2팀 vs 3팀)", fontweight='bold', fontsize=13)
ax2.set_xticks(x + width / 2)
ax2.set_xticklabels(APIS, fontsize=11)
ax2.set_ylabel("평균 응답시간 (ms)")
ax2.set_xlabel("API")
ax2.set_ylim(0, 600)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
output2 = BASE_DIR / "processed" / "day7_bar_100users.png"
plt.savefig(output2, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 막대그래프 저장 완료: {output2}")