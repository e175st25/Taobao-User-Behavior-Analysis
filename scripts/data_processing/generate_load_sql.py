from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLIT_FOLDER = PROJECT_ROOT / "data" / "split"

OUTPUT_FILE = PROJECT_ROOT / "sql" / "load_all_1_101.sql"

START = 1
END = 101

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for i in range(START, END + 1):

        csv_path = (SPLIT_FOLDER / f"user_behavior_part_{i:03d}.csv").as_posix()

        f.write(f"""-- ==========================================
-- Part {i:03d}
-- ==========================================

LOAD DATA LOCAL INFILE
'{csv_path}'
INTO TABLE taobao.user_behavior_raw
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\r\\n'
IGNORE 1 LINES
(
    user_id,
    item_id,
    category_id,
    behavior_type,
    timestamp,
    datetime,
    date,
    hour,
    weekday
);

\n""")

print(f"✅ 已生成：{OUTPUT_FILE}")
print(f"共生成 {END - START + 1} 条 LOAD DATA 语句")