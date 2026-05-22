import pandas as pd

# 2팀 CSV 확인
team2_csv = pd.read_csv("load_test/raw_data/team2/csv_results/test10_result.csv")
print("=== 2팀 CSV 컬럼 ===")
print(team2_csv.columns)
print(team2_csv.head())

# 2팀 XML 확인
team2_xml = pd.read_xml(
    "load_test/raw_data/team2/xml_results/result10.xml",
    xpath=".//httpSample"
)
print("\n=== 2팀 XML 컬럼 ===")
print(team2_xml.columns)
print(team2_xml.head())

# 3팀 CSV 확인
team3_csv = pd.read_csv("load_test/raw_data/team3/csv_summary/summary10_data.csv")
print("\n=== 3팀 CSV 컬럼 ===")
print(team3_csv.columns)
print(team3_csv.head())

# 3팀 Excel 확인
team3_excel = pd.read_excel("load_test/raw_data/team3/excel_results/test10.xlsx")
print("\n=== 3팀 Excel 컬럼 ===")
print(team3_excel.columns)
print(team3_excel.head())