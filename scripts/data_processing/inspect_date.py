import pandas as pd

file_path = "UserBehavior.csv"

columns = [
    "user_id",
    "item_id",
    "category_id",
    "behavior_type",
    "timestamp"
]

chunk_size = 1_000_000

start_timestamp = 1511539200
end_timestamp = 1512316799

total_rows = 0
valid_rows = 0
invalid_rows = 0

too_early_rows = 0
too_late_rows = 0

invalid_samples = []

for chunk in pd.read_csv(
    file_path,
    header=None,
    names=columns,
    chunksize=chunk_size
):
    total_rows += len(chunk)

    valid_mask = chunk["timestamp"].between(
        start_timestamp,
        end_timestamp
    )

    valid_rows += valid_mask.sum()
    invalid_rows += (~valid_mask).sum()

    too_early_rows += (
        chunk["timestamp"] < start_timestamp
    ).sum()

    too_late_rows += (
        chunk["timestamp"] > end_timestamp
    ).sum()

    # 保存少量异常样本
    if len(invalid_samples) < 20:
        sample = chunk.loc[
            ~valid_mask,
            columns
        ].head(20 - len(invalid_samples))

        invalid_samples.extend(
            sample.to_dict("records")
        )

print("总行数：", total_rows)
print("有效时间记录：", valid_rows)
print("异常时间记录：", invalid_rows)
print("早于有效范围：", too_early_rows)
print("晚于有效范围：", too_late_rows)

print("\n异常记录占比：")
print(f"{invalid_rows / total_rows:.6%}")

print("\n异常记录样本：")
for row in invalid_samples:
    row["datetime"] = pd.to_datetime(
        row["timestamp"],
        unit="s",
        errors="coerce"
    )
    print(row)