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

total_rows = 0
missing_values = pd.Series(0, index=columns)
behavior_counts = pd.Series(dtype="int64")
min_timestamp = None
max_timestamp = None

for chunk in pd.read_csv(
    file_path,
    header=None,
    names=columns,
    chunksize=chunk_size
):
    total_rows += len(chunk)

    missing_values = missing_values.add(
        chunk.isna().sum(),
        fill_value=0
    )

    behavior_counts = behavior_counts.add(
        chunk["behavior_type"].value_counts(),
        fill_value=0
    )

    valid_chunk = chunk[
        chunk["timestamp"].between(1511539200, 1512316799)
    ]

    if not valid_chunk.empty:
        chunk_min = valid_chunk["timestamp"].min()
        chunk_max = valid_chunk["timestamp"].max()

        min_timestamp = (
            chunk_min
            if min_timestamp is None
            else min(min_timestamp, chunk_min)
        )

        max_timestamp = (
            chunk_max
            if max_timestamp is None
            else max(max_timestamp, chunk_max)
        )

print("总行数：", total_rows)

print("\n缺失值数量：")
print(missing_values.astype("int64"))

print("\n行为类型数量：")
print(behavior_counts.astype("int64").sort_index())

print("\n最早时间：")
print(pd.to_datetime(min_timestamp, unit="s"))

print("\n最晚时间：")
print(pd.to_datetime(max_timestamp, unit="s"))