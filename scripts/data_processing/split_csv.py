    import pandas as pd
    import os

    input_file = "UserBehavior.csv"
    output_folder = "../split"

    os.makedirs(output_folder, exist_ok=True)

    chunk_size = 1_000_000

    for i, chunk in enumerate(
        pd.read_csv(
            input_file,
            header=None,
            names=[
                "user_id",
                "item_id",
                "category_id",
                "behavior_type",
                "timestamp"
            ],
            chunksize=chunk_size
        )
    ):

        # ===== 新增时间字段 =====
        chunk["datetime"] = pd.to_datetime(
            chunk["timestamp"],
            unit="s",
            errors="coerce"
        )

        chunk["date"] = chunk["datetime"].dt.date
        chunk["hour"] = chunk["datetime"].dt.hour
        chunk["weekday"] = chunk["datetime"].dt.weekday

        filename = os.path.join(
            output_folder,
            f"user_behavior_part_{i+1:03d}.csv"
        )

        chunk.to_csv(
            filename,
            index=False
        )

        print(f"Saved {filename}")