import os
import re
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# =====================================================
# 1. [경로 해결] Git 레포지토리 루트 기준 절대경로 고정
# =====================================================
# 실행하는 위치(cwd)나 스크립트 위치에 구애받지 않도록 상위 탐색으로 'QA-1-TEAM' 루트를 잡습니다.
START_DIR = os.path.dirname(os.path.abspath(__file__))

def get_repo_root(path):
    current = path
    # 위로 5단계까지 올라가며 load_test 폴더가 있는 진짜 루트를 추적
    for _ in range(5):
        if os.path.isdir(os.path.join(current, "load_test")):
            return current
        parent = os.path.dirname(current)
        if parent == current: # 더 이상 올라갈 곳이 없을 때 복귀
            break
        current = parent
    return os.path.abspath(os.path.join(path, "..")) # 실패 시 한 단계 위를 루트로 가정

REPO_ROOT = get_repo_root(START_DIR)

# 레포 루트 기준으로 raw_data 및 결과 저장 경로 강제 매핑
RAW_DATA_ROOT = os.path.join(REPO_ROOT, "load_test", "raw_data")
TEAM2_DIR = os.path.join(RAW_DATA_ROOT, "team2")
TEAM3_DIR = os.path.join(RAW_DATA_ROOT, "team3")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output")

# 출력 폴더 자동 생성
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print(f"🚀 [확정된 레포지토리 루트] {REPO_ROOT}")
print(f"📂 [감시할 raw_data 경로]  {RAW_DATA_ROOT}")
print(f"📂 [2팀 데이터 타겟]       {TEAM2_DIR}")
print(f"📂 [3팀 데이터 타겟]       {TEAM3_DIR}")
print(f"📊 [리포트 그래프 저장]    {OUTPUT_DIR}")
print("=" * 60)

# =====================================================
# 2. 한글 깨짐 방지 서식 및 라벨 맵핑
# =====================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  

USER_GROUPS = ["10", "30", "50", "70", "100"]

LABEL_UNIFICATION_MAP = {
    "auth": "Auth - Login", "1. 과목 정보": "API 1 - 과목 정보", "2. 시험 입장": "API 2 - 시험 입장",
    "3. 시험 시작": "API 3 - 시험 시작", "4. 시험 제출": "API 4 - 시험 제출", "5. 재응시": "API 5 - 재응시",
    "auth - login": "Auth - Login", "api 1 - 과목 정보": "API 1 - 과목 정보", "api 2 - 시험 입장": "API 2 - 시험 입장",
    "api 3 - 시험 시작": "API 3 - 시험 시작", "api 4 - 시험 제출": "API 4 - 시험 제출", "api 5 - 재응시": "API 5 - 재응시"
}

# =====================================================
# 3. 2팀/3팀 포맷 통합 멀티 파서 엔진 (XML 구조 완전 대응)
# =====================================================
def parse_xml_to_df(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        records = []
        for child in root:
            if child.tag in ['httpSample', 'sample']:
                attr = child.attrib
                records.append({
                    "timestamp": attr.get("ts"),
                    "elapsed_ms": attr.get("t"),
                    "success": attr.get("s"), 
                    "label": attr.get("lb")
                })
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()

def load_and_standardize_team_data(target_dir, group_keyword):
    if not os.path.exists(target_dir):
        return pd.DataFrame()
    
    file_dfs = []
    target_columns = ["timestamp", "elapsed_ms", "success", "label"]
    
    for root_dir, dirs, files in os.walk(target_dir):
        for f in files:
            # 파일명에 포함된 숫자와 인원수 정확히 대조 (10명 조건에 100명 파일 오동작 방지)
            numbers_in_name = re.findall(r'\d+', f)
            if group_keyword in numbers_in_name:
                file_path = os.path.join(root_dir, f)
                df = pd.DataFrame()
                ext = f.lower()
                
                try:
                    if ext.endswith('.csv'):
                        df = pd.read_csv(file_path, encoding='utf-8-sig', on_bad_lines='skip')
                    elif ext.endswith('.xlsx') or ext.endswith('.xls'):
                        df = pd.read_excel(file_path, engine='openpyxl')
                    elif ext.endswith('.xml'):
                        df = parse_xml_to_df(file_path)
                except Exception:
                    continue
                    
                if df.empty:
                    continue
                    
                df.columns = [str(c).strip().lower() for c in df.columns]
                df = df.rename(columns={"ts": "timestamp", "t": "elapsed_ms", "elapsed": "elapsed_ms", "s": "success", "lb": "label"})
                df = df[[c for c in target_columns if c in df.columns]]
                
                if "label" in df.columns:
                    df["label"] = df["label"].astype(str).str.strip().apply(lambda x: LABEL_UNIFICATION_MAP.get(x, LABEL_UNIFICATION_MAP.get(x.lower(), x)))
                
                file_dfs.append(df)
                
    if file_dfs:
        integrated_df = pd.concat(file_dfs, axis=0, ignore_index=True)
        integrated_df['timestamp'] = pd.to_numeric(integrated_df['timestamp'], errors='coerce')
        integrated_df['elapsed_ms'] = pd.to_numeric(integrated_df['elapsed_ms'], errors='coerce')
        return integrated_df.dropna(subset=['timestamp'])
        
    return pd.DataFrame()

# =====================================================
# 4. 연산 및 정밀 검산
# =====================================================
analysis_results = []
print("조별 테스트 데이터 연산 가동...")

for group in USER_GROUPS:
    # --- 2팀 연산 ---
    df_team2 = load_and_standardize_team_data(TEAM2_DIR, group)
    t2_avg_tps, t2_error_rate = 0.0, 0.0
    if not df_team2.empty:
        df_team2["second"] = pd.to_datetime(df_team2["timestamp"], unit="ms").dt.floor("s")
        t2_avg_tps = df_team2.groupby("second").size().mean()
        
        success_series = df_team2["success"].astype(str).str.strip().str.lower()
        t2_error_count = len(df_team2[success_series != "true"])
        t2_error_rate = (t2_error_count / len(df_team2)) * 100
        
    # --- 3팀 연산 ---
    df_team3 = load_and_standardize_team_data(TEAM3_DIR, group)
    t3_avg_tps, t3_error_rate = 0.0, 0.0
    if not df_team3.empty:
        df_team3["second"] = pd.to_datetime(df_team3["timestamp"], unit="ms").dt.floor("s")
        t3_avg_tps = df_team3.groupby("second").size().mean()
        
        success_series_t3 = df_team3["success"].astype(str).str.strip().str.lower()
        t3_error_count = len(df_team3[success_series_t3 != "true"])
        t3_error_rate = (t3_error_count / len(df_team3)) * 100

    analysis_results.append({
        "users": group + "명",
        "t2_tps": round(t2_avg_tps, 2), "t2_err": round(t2_error_rate, 4),
        "t3_tps": round(t3_avg_tps, 2), "t3_err": round(t3_error_rate, 4)
    })

# =====================================================
# 5. 이중 축 시각화 결과 도출
# =====================================================
if analysis_results and any(r["t2_tps"] > 0 or r["t3_tps"] > 0 for r in analysis_results):
    summary_df = pd.DataFrame(analysis_results)
    x_indices = np.arange(len(summary_df["users"]))
    bar_width = 0.35  
    
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # 좌측 축: TPS 막대
    color_tps_axis = '#2c3e50'
    ax1.set_xlabel("동시 접속 사용자 수", fontsize=12, labelpad=12, fontweight='bold')
    ax1.set_ylabel("평균 TPS (초당 처리 건수)", color=color_tps_axis, fontsize=12, labelpad=12, fontweight='bold')
    
    bars_t2 = ax1.bar(x_indices - bar_width/2, summary_df["t2_tps"], color='#5dade2', alpha=0.9, width=bar_width, label="2팀 평균 TPS")
    bars_t3 = ax1.bar(x_indices + bar_width/2, summary_df["t3_tps"], color='#52be80', alpha=0.9, width=bar_width, label="3팀 평균 TPS")
    ax1.tick_params(axis='y', labelcolor=color_tps_axis)
    
    tps_max = summary_df[["t2_tps","t3_tps"]].max().max()
    tps_offset = tps_max * 0.015 if tps_max > 0 else 1
    ax1.set_ylim(0, tps_max * 1.15 if tps_max > 0 else 10)
    
    for bar in bars_t2:
        h = bar.get_height()
        if h > 0: ax1.text(bar.get_x() + bar.get_width()/2.0, h + tps_offset, f'{h}', ha='center', va='bottom', color='#1f618d', fontsize=9, fontweight='bold')
    for bar in bars_t3:
        h = bar.get_height()
        if h > 0: ax1.text(bar.get_x() + bar.get_width()/2.0, h + tps_offset, f'{h}', ha='center', va='bottom', color='#1e8449', fontsize=9, fontweight='bold')
        
    # 우측 축: 에러율 꺾은선
    ax2 = ax1.twinx()
    color_err_axis = '#7b241c'
    ax2.set_ylabel("에러율 (%)", color=color_err_axis, fontsize=12, labelpad=12, fontweight='bold')
    
    line_t2 = ax2.plot(summary_df["users"], summary_df["t2_err"], marker='o', linestyle='--', color='#ec7063', linewidth=2, markersize=7, label="2팀 에러율 (%)")
    line_t3 = ax2.plot(summary_df["users"], summary_df["t3_err"], marker='s', linestyle='--', color='#af7ac5', linewidth=2, markersize=7, label="3팀 에러율 (%)")
    ax2.tick_params(axis='y', labelcolor=color_err_axis)
    
    err_max = summary_df[["t2_err", "t3_err"]].max().max()
    err_offset = err_max * 0.03 if err_max > 0 else 0.01
    
    for idx, row in summary_df.iterrows():
        ax2.text(idx - 0.12, row["t2_err"] + err_offset, f'{round(row["t2_err"], 2)}%', ha='right', va='bottom', color='#b03a2e', fontsize=9, fontweight='bold')
        ax2.text(idx + 0.12, row["t3_err"] + err_offset, f'{round(row["t3_err"], 2)}%', ha='left', va='bottom', color='#6c3483', fontsize=9, fontweight='bold')
        
    ax2.set_ylim(-0.01, err_max * 1.3 if err_max > 0 else 0.5)
        
    plt.title("조별 부하 테스트 성능 대조군: 2팀 vs 3팀 TPS 및 에러율 비교 추이", fontsize=15, pad=22, fontweight='bold')
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels(summary_df["users"], fontsize=11)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    all_elements = [bars_t2, bars_t3, line_t2[0], line_t3[0]]
    labels = [el.get_label() for el in all_elements]
    ax1.legend(all_elements, labels, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, fontsize=10, frameon=True, shadow=True)
    
    fig.tight_layout()
    final_chart_path = os.path.join(OUTPUT_DIR, "team2_vs_team3_final_fixed.png")
    plt.savefig(final_chart_path, dpi=150)
    
    print("\n" + "="*50)
    print(f"🎉 [성공] 경로 매핑 정상 가동 완료!")
    print(f"💾 결과 레포트 파일: {final_chart_path}")
    print("="*50)
else:
    print("\n⚠️ 탐색된 파일은 있으나 유효한 성능 데이터 지표 추출에 실패했습니다.")