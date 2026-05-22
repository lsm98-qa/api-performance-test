from pathlib import Path
import csv
import re

BASE_DIR = Path(__file__).resolve().parents[1]

team2_files = {
    10: BASE_DIR / "raw_data" / "team2" / "csv_results" / "test10_result.csv",
    30: BASE_DIR / "raw_data" / "team2" / "csv_results" / "test30_result.csv",
    50: BASE_DIR / "raw_data" / "team2" / "csv_results" / "test50_result.csv",
    70: BASE_DIR / "raw_data" / "team2" / "csv_results" / "test70_result.csv",
    100: BASE_DIR / "raw_data" / "team2" / "csv_results" / "test100_result.csv",
}

team3_files = {
    10: BASE_DIR / "raw_data" / "team3" / "csv_summary" / "summary10_data.csv",
    30: BASE_DIR / "raw_data" / "team3" / "csv_summary" / "summary30_data.csv",
    50: BASE_DIR / "raw_data" / "team3" / "csv_summary" / "summary50_data.csv",
    70: BASE_DIR / "raw_data" / "team3" / "csv_summary" / "summary70_data.csv",
    100: BASE_DIR / "raw_data" / "team3" / "csv_summary" / "summary100_data.csv",
}

def normalize_api(label: str) -> str:
    label = str(label).strip()
    mapping = {
        "Auth": "Auth",
        "Auth - Login": "Auth",
        "1. 과목 정보": "과목 정보",
        "API 1 - 과목 정보": "과목 정보",
        "2. 시험 입장": "시험 입장",
        "API 2 - 시험 입장": "시험 입장",
        "3. 시험 시작": "시험 시작",
        "API 3 - 시험 시작": "시험 시작",
        "4. 시험 제출": "시험 제출",
        "API 4 - 시험 제출": "시험 제출",
        "5. 재응시": "재응시",
        "API 5 - 재응시": "재응시",
    }
    if label in mapping:
        return mapping[label]

    label = re.sub(r"^API\s*\d+\s*-\s*", "", label)
    label = re.sub(r"^\d+\.\s*", "", label)
    return label.strip()

def parse_percent(value):
    text = str(value).strip().replace("%", "")
    try:
        return float(text)
    except ValueError:
        return None

def parse_float(value):
    text = str(value).strip().replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None

def read_summary_csv(path: Path, team: str, users: int):
    rows = []

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row.get("Label", "").strip()
            if not label:
                continue

            rows.append({
                "team": team,
                "users": users,
                "api": normalize_api(label),
                "original_label": label,
                "samples": parse_float(row.get("# Samples")),
                "avg_latency_ms": parse_float(row.get("Average")),
                "min_latency_ms": parse_float(row.get("Min")),
                "max_latency_ms": parse_float(row.get("Max")),
                "std_dev_ms": parse_float(row.get("Std. Dev.")),
                "error_rate_percent": parse_percent(row.get("Error %")),
                "throughput_tps": parse_float(row.get("Throughput")),
                "source_file": path.name,
            })

    return rows

def main():
    all_rows = []

    for users, path in team2_files.items():
        all_rows.extend(read_summary_csv(path, "team2", users))

    for users, path in team3_files.items():
        all_rows.extend(read_summary_csv(path, "team3", users))

    output_dir = BASE_DIR / "processed"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "unified_summary.csv"

    headers = [
        "team",
        "users",
        "api",
        "original_label",
        "samples",
        "avg_latency_ms",
        "min_latency_ms",
        "max_latency_ms",
        "std_dev_ms",
        "error_rate_percent",
        "throughput_tps",
        "source_file",
    ]

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"생성 완료: {output_path}")
    print(f"총 {len(all_rows)}개 행이 저장되었습니다.")

if __name__ == "__main__":
    main()
