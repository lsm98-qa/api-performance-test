# -*- coding: utf-8 -*-
"""
Day 7 - 병목 후보 시각화 (각각 별도 파일)
실행: python load_test/scripts/day7_bottleneck_graphs.py
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
COLORS = {"team2": "#4C72B0", "team3": "#DD8452"}


# ===========================
# 그래프 1 — 2팀 시험 제출
# ===========================
fig1, ax1 = plt.subplots(figsize=(8, 5))
data = df[(df["team"] == "team2") & (df["api"] == "시험 제출")].sort_values("users")

ax1.plot(data["users"], data["avg_latency_ms"], marker='o', color="#4C72B0",
         label="Avg Latency", linewidth=2, markersize=7)
ax1.plot(data["users"], data["max_latency_ms"], marker='s', color="#FF4444",
         label="Max Latency", linewidth=2, markersize=7)
ax1.fill_between(
    data["users"],
    data["avg_latency_ms"] - data["std_dev_ms"],
    data["avg_latency_ms"] + data["std_dev_ms"],
    alpha=0.2, color="#4C72B0", label="Avg ± Std Dev"
)
for _, row in data.iterrows():
    ax1.annotate(f"{int(row['max_latency_ms'])}ms",
                xy=(row['users'], row['max_latency_ms']),
                xytext=(0, 8), textcoords='offset points',
                ha='center', fontsize=9, color="#FF4444", fontweight='bold')

y_max = max(data["max_latency_ms"].max(), data["avg_latency_ms"].max()) * 1.2
ax1.set_ylim(0, y_max)
ax1.set_title("Team2 시험 제출 — Avg/Max/Std Dev 추이", fontweight='bold', fontsize=12)
ax1.set_xlabel("동시 사용자 수 (명)")
ax1.set_ylabel("응답시간 (ms)")
ax1.set_xticks(USERS)
ax1.legend()
ax1.grid(True, alpha=0.3)
plt.tight_layout()
out1 = BASE_DIR / "processed" / "day7_bottleneck_exam_submit.png"
plt.savefig(out1, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 저장 완료: {out1}")


# ===========================
# 그래프 2 — 2팀 재응시
# ===========================
fig2, ax2 = plt.subplots(figsize=(8, 5))
data2 = df[(df["team"] == "team2") & (df["api"] == "재응시")].sort_values("users")

ax2.plot(data2["users"], data2["avg_latency_ms"], marker='o', color="#4C72B0",
         label="Avg Latency", linewidth=2, markersize=7)
ax2.plot(data2["users"], data2["max_latency_ms"], marker='s', color="#FF4444",
         label="Max Latency", linewidth=2, markersize=7)
ax2.fill_between(
    data2["users"],
    data2["avg_latency_ms"] - data2["std_dev_ms"],
    data2["avg_latency_ms"] + data2["std_dev_ms"],
    alpha=0.2, color="#4C72B0", label="Avg ± Std Dev"
)
for _, row in data2.iterrows():
    ax2.annotate(f"{int(row['max_latency_ms'])}ms",
                xy=(row['users'], row['max_latency_ms']),
                xytext=(0, 8), textcoords='offset points',
                ha='center', fontsize=9, color="#FF4444", fontweight='bold')

y_max2 = max(data2["max_latency_ms"].max(), data2["avg_latency_ms"].max()) * 1.2
ax2.set_ylim(0, y_max2)
ax2.set_title("Team2 재응시 — Avg/Max 추이", fontweight='bold', fontsize=12)
ax2.set_xlabel("동시 사용자 수 (명)")
ax2.set_ylabel("응답시간 (ms)")
ax2.set_xticks(USERS)
ax2.legend()
ax2.grid(True, alpha=0.3)
plt.tight_layout()
out2 = BASE_DIR / "processed" / "day7_bottleneck_retry.png"
plt.savefig(out2, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 저장 완료: {out2}")


# ===========================
# 그래프 3 — TPS 비교
# ===========================
fig3, ax3 = plt.subplots(figsize=(8, 5))

all_tps = []
for team, color in COLORS.items():
    team_data = df[df["team"] == team].groupby("users")["throughput_tps"].mean().reset_index()
    team_data = team_data.sort_values("users")
    ax3.plot(team_data["users"], team_data["throughput_tps"],
             marker='o', color=color, label=team, linewidth=2, markersize=7)
    for _, row in team_data.iterrows():
        ax3.annotate(f"{row['throughput_tps']:.3f}",
                    xy=(row['users'], row['throughput_tps']),
                    xytext=(0, 8), textcoords='offset points',
                    ha='center', fontsize=9, color=color, fontweight='bold')
    all_tps.extend(team_data["throughput_tps"].tolist())

y_max3 = max(all_tps) * 1.2
ax3.set_ylim(0, y_max3)
ax3.set_title("TPS Trend — Team2 vs Team3", fontweight='bold', fontsize=12)
ax3.set_xlabel("동시 사용자 수 (명)")
ax3.set_ylabel("TPS (req/sec)")
ax3.set_xticks(USERS)
ax3.legend()
ax3.grid(True, alpha=0.3)
plt.tight_layout()
out3 = BASE_DIR / "processed" / "day7_bottleneck_tps.png"
plt.savefig(out3, dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 저장 완료: {out3}")