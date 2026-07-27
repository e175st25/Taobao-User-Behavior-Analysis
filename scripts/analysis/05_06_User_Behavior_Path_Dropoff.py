#%%
from pathlib import Path
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_OUTPUT_DIR = PROJECT_ROOT / "sql"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures" / "chapter5"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

user_summary = pd.read_csv(
    SQL_OUTPUT_DIR / "user_behavior_summary.csv"
)

#用户行为覆盖率
# %%
user_journey = (
    user_summary
    .groupby("behavior_type")["user_id"]
    .nunique()
    .reset_index()
)

user_journey.columns = [
    "behavior",
    "users"
]

print(user_journey)

#画图
# %%
behavior_order = [
    "pv",
    "fav",
    "cart",
    "buy"
]


user_journey["behavior"] = pd.Categorical(
    user_journey["behavior"],
    categories=behavior_order,
    ordered=True
)

user_journey = (
    user_journey
    .sort_values("behavior")
)


plt.figure(figsize=(8,5))

bars = plt.bar(
    user_journey["behavior"],
    user_journey["users"]
)

plt.xlabel("Behavior Stage")
plt.ylabel("Number of Users")
plt.title("User Coverage Across Shopping Journey")


for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x()+bar.get_width()/2,
        height,
        f"{height/1000000:.2f}M",
        ha="center",
        va="bottom"
    )


plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "user_behavior_journey.png"
)

plt.show()

#用户行为路径
# %%
behavior_order = {
    "pv":1,
    "fav":2,
    "cart":3,
    "buy":4
}


def sort_path(x):
    return " → ".join(
        sorted(
            x,
            key=lambda i: behavior_order[i]
        )
    )


user_path = (
    user_summary
    .groupby("user_id")["behavior_type"]
    .unique()
    .apply(sort_path)
    .reset_index()
)

user_path.columns = [
    "user_id",
    "path"
]

path_summary = (
    user_path["path"]
    .value_counts()
    .head(10)
)

print(path_summary)

#Top 8 绘图
# %%
path_summary = (
    user_path["path"]
    .value_counts()
    .head(8)
    .sort_values()
)


plt.figure(figsize=(10,6))

plt.barh(
    path_summary.index,
    path_summary.values
)

plt.xlabel("Number of Users")
plt.ylabel("Behavior Path")
plt.title("Most Common User Behavior Paths")

for i, value in enumerate(path_summary.values):
    plt.text(
        value,
        i,
        f"{value:,}",
        va="center"
    )

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "top_behavior_paths.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#Chapter6
# %%
FIGURES_DIR = PROJECT_ROOT / "figures" / "chapter6"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# %%
top_paths = (
    user_path["path"]
    .value_counts()
    .head(8)
)

behavior_order = [
    "pv",
    "fav",
    "cart",
    "buy"
]

#循环计算路径
# %%
path_conversion = []

for path in top_paths.index:

    # 当前路径用户
    users = user_path[
        user_path["path"] == path
    ]["user_id"]


    # 这些用户的行为记录
    user_behavior = (
        user_summary[
            user_summary["user_id"].isin(users)
        ]
        .groupby("behavior_type")["user_id"]
        .nunique()
    )


    row = {
        "path": path,
        "users": len(users)
    }


    # 每个阶段用户数
    for behavior in behavior_order:
        row[behavior] = user_behavior.get(
            behavior,
            0
        )


    path_conversion.append(row)


path_conversion = pd.DataFrame(
    path_conversion
)

print(path_conversion)

#计算conversion rate和最终购买率
# %%
path_counts = user_path["path"].value_counts()

dropoff_summary = pd.DataFrame({
    "path_stage": [
        "pv",
        "pv → cart",
        "pv → fav",
        "pv → fav → cart"
    ],
    "converted_path": [
        "pv → buy",
        "pv → cart → buy",
        "pv → fav → buy",
        "pv → fav → cart → buy"
    ],
    "stopped_users": [
        path_counts.get("pv", 0),
        path_counts.get("pv → cart", 0),
        path_counts.get("pv → fav", 0),
        path_counts.get("pv → fav → cart", 0)
    ],
    "converted_users": [
        path_counts.get("pv → buy", 0),
        path_counts.get("pv → cart → buy", 0),
        path_counts.get("pv → fav → buy", 0),
        path_counts.get("pv → fav → cart → buy", 0)
    ]
})

dropoff_summary["total_users"] = (
    dropoff_summary["stopped_users"]
    + dropoff_summary["converted_users"]
)

dropoff_summary["conversion_rate"] = (
    dropoff_summary["converted_users"]
    / dropoff_summary["total_users"]
)

dropoff_summary["dropoff_rate"] = (
    dropoff_summary["stopped_users"]
    / dropoff_summary["total_users"]
)

print(dropoff_summary)

#保存
# %%
dropoff_summary.to_csv(
    PROCESSED_DATA_DIR / "dropoff_summary.csv",
    index=False
)

#绘图
# %%
import matplotlib.pyplot as plt

for _, row in dropoff_summary.iterrows():

    labels = ["Converted", "Dropped"]
    values = [
        row["converted_users"],
        row["stopped_users"]
    ]

    plt.figure(figsize=(7, 5))

    bars = plt.bar(
        labels,
        values
    )

    plt.ylabel("Number of Users")
    plt.xlabel("User Outcome")

    plt.title(
        f"User Conversion After {row['path_stage']}"
    )

    # 在柱子上显示用户数量
    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{int(value):,}",
            ha="center",
            va="bottom"
        )

    # 在图片内部显示转化率和流失率
    plt.text(
        0.02,
        0.95,
        f"Conversion Rate: {row['conversion_rate']:.2%}\n"
        f"Drop-off Rate: {row['dropoff_rate']:.2%}",
        transform=plt.gca().transAxes,
        ha="left",
        va="top"
    )

    plt.tight_layout()

    file_name = (
        row["path_stage"]
        .replace(" → ", "_")
        .replace(" ", "_")
    )

    plt.savefig(
        FIGURES_DIR / f"dropoff_{file_name}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    
# %%
for _, row in dropoff_summary.iterrows():

    labels = [
        row["path_stage"],
        row["converted_path"]
    ]

    values = [
        row["total_users"],
        row["converted_users"]
    ]

    plt.figure(figsize=(8, 5))

    plt.plot(
        labels,
        values,
        marker="o",
        linewidth=2
    )

    for x, value in enumerate(values):
        plt.text(
            x,
            value,
            f"{int(value):,}",
            ha="center",
            va="bottom"
        )

    plt.ylabel("Number of Users")
    plt.xlabel("Path Stage")

    plt.title(
        f"User Retention Along {row['path_stage']} Path"
    )

    plt.ylim(
        0,
        max(values) * 1.2
    )

    plt.text(
        0.02,
        0.95,
        f"Conversion Rate: {row['conversion_rate']:.2%}\n"
        f"Drop-off Rate: {row['dropoff_rate']:.2%}",
        transform=plt.gca().transAxes,
        ha="left",
        va="top"
    )

    plt.tight_layout()

    file_name = (
        row["path_stage"]
        .replace(" → ", "_")
        .replace(" ", "_")
    )

    plt.savefig(
        FIGURES_DIR / f"path_retention_{file_name}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()