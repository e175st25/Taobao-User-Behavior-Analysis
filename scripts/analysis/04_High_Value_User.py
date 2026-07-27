#%%
from pathlib import Path
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_OUTPUT_DIR = PROJECT_ROOT / "sql"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures" / "chapter4"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

#导入数据
user_summary = pd.read_csv(
    SQL_OUTPUT_DIR / "behavior总表.csv"
)

print(user_summary.head())

#转换长表
#%%
user_behavior_summary = (
    user_summary
    .groupby(
        ["user_id", "behavior_type"]
    )
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
user_behavior_summary.columns.name = None

print(user_behavior_summary.head())
print(user_behavior_summary.columns.tolist())

#用户购买统计分布
#%%
print(user_behavior_summary["buy"].describe())
print(
    user_behavior_summary["buy"].quantile(
        [0.25, 0.5, 0.75, 0.90, 0.95, 0.99]
    )
)

#绘图 限制在99% 也就是buy=11
# %%
buy_counts = (
    user_behavior_summary["buy"]
    .value_counts()
    .sort_index()
)

buy_counts = buy_counts.loc[:11]      # 只显示前99%的范围

plt.figure(figsize=(10, 6))

bars = plt.bar(
    buy_counts.index,
    buy_counts.values,
    edgecolor="black"
)

plt.xlabel("Purchase Count")
plt.ylabel("Number of Users")
plt.title("Distribution of Purchase Count per User")

plt.xticks(range(12))

# 在柱子上添加人数
for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height,
        f"{height:,}",
        ha="center",
        va="bottom",
        fontsize=8,
        rotation=0
    )

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "purchase_count_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#RF analysis
#最后一天购买 → Recency=1
#第一天购买 → Recency=9
# %%
buy_summary = user_summary[
    user_summary["behavior_type"] == "buy"
].copy()

user_rf = (
    buy_summary
    .groupby("user_id")
    .agg(
        frequency=("count(behavior_type)", "sum"),
        last_purchase_time=("last_behavior_time", "max")
    )
    .reset_index()
)

user_rf["last_purchase_time"] = pd.to_datetime(
    user_rf["last_purchase_time"]
)

reference_date = (
    user_rf["last_purchase_time"].max()
    + pd.Timedelta(days=1)
)

user_rf["recency"] = (
    reference_date -
    user_rf["last_purchase_time"]
).dt.days

print(user_rf.head())
print(user_rf.describe())

#672404/987991=68.1% 用户至少购买一次

#visualization
# %%
user_rf["frequency"].quantile(
    [0.9,0.95,0.99]
)

# %%
from matplotlib.colors import LogNorm

rf_matrix = (
    user_rf
    .groupby(
        ["frequency", "recency"]
    )
    .size()
    .unstack(
        fill_value=0
    )
)

rf_matrix = rf_matrix.loc[
    rf_matrix.index <= 14
]

rf_matrix = rf_matrix.sort_index(ascending=False)

plt.figure(figsize=(10,8))

#使用log transformation用来更好展示用户RF分布
#显示小群体
plt.imshow(
    rf_matrix,
    aspect="auto",
    cmap="YlOrRd",
    norm=LogNorm()
)

plt.colorbar(
    label="Number of Users"
)

plt.xlabel("Recency")
plt.ylabel("Frequency")
plt.title("RF Segmentation of Purchasing Users")

plt.xticks(
    range(len(rf_matrix.columns)),
    rf_matrix.columns
)

plt.yticks(
    range(len(rf_matrix.index)),
    rf_matrix.index
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "rf_segmentation_purchasing_users.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#Top User Analysis
# %%
top_users = (
    user_rf
    .sort_values(
        by="frequency",
        ascending=False
    )
    .head(20)
)

print(top_users)

#绘图
# %%
plt.figure(figsize=(10, 6))

plt.barh(
    top_users["user_id"].astype(str),
    top_users["frequency"]
)

plt.xlabel("Purchase Count")
plt.ylabel("User ID")
plt.title("Top 20 Users by Purchase Frequency")

plt.gca().invert_yaxis()

for i, value in enumerate(top_users["frequency"]):
    plt.text(
        value,
        i,
        f"{value}",
        va="center"
    )

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "top20_users_purchase_frequency.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#高价值用户
# %%
pareto_df = (
    user_rf
    .sort_values(
        by="frequency",
        ascending=False
    )
    .reset_index(drop=True)
)

#计算累计比例
total_purchases = pareto_df["frequency"].sum()

pareto_df["cumulative_purchases"] = (
    pareto_df["frequency"]
    .cumsum()
)

pareto_df["purchase_percentage"] = (
    pareto_df["cumulative_purchases"]
    / total_purchases
)

pareto_df["user_percentage"] = (
    (pareto_df.index + 1)
    / len(pareto_df)
)

for pct in [0.1, 0.2, 0.5]:

    purchase_share = (
        pareto_df
        .iloc[
            :int(len(pareto_df)*pct)
        ]["frequency"]
        .sum()
        /
        total_purchases
    )

    print(
        f"Top {pct*100:.0f}% users contribute "
        f"{purchase_share*100:.2f}% of purchases"
    )

#Top 10% users contribute 31.09% of purchases
#Top 20% users contribute 47.88% of purchases
#Top 50% users contribute 77.98% of purchases

#绘图
# %%
plt.figure(figsize=(10, 6))

plt.plot(
    pareto_df["user_percentage"] * 100,
    pareto_df["purchase_percentage"] * 100
)

# 参考线：完全平均贡献
plt.plot(
    [0, 100],
    [0, 100],
    linestyle="--"
)

plt.xlabel("Percentage of Users (%)")
plt.ylabel("Percentage of Purchases (%)")

plt.title(
    "Pareto Analysis of User Purchase Contribution"
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "pareto_purchase_contribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#用户分层
#根据之前的结果：low:1 regular:2-4 high-value:5-14 VIP:14+
#4次对应75%分位 14次对应99%分位
# %%
def assign_segment(freq):
    if freq == 1:
        return "Low"
    elif freq <= 4:
        return "Regular"
    elif freq <= 14:
        return "High-value"
    else:
        return "VIP"


user_rf["segment"] = (
    user_rf["frequency"]
    .apply(assign_segment)
)

segment_summary = (
    user_rf["segment"]
    .value_counts()
    .reset_index()
)

segment_summary.columns = [
    "segment",
    "users"
]

print(segment_summary)

#      segment   users
#0     Regular  321624
#1         Low  228546
#2  High-value  116760
#3         VIP    5474

#绘图
# %%
plt.figure(figsize=(8,5))

bars = plt.barh(
    segment_summary["segment"],
    segment_summary["users"]
)

plt.xlabel("Number of Users")
plt.ylabel("Segment")
plt.title("User Segmentation Based on Purchase Frequency")

plt.gca().invert_yaxis()

for bar in bars:
    width = bar.get_width()

    plt.text(
        width,
        bar.get_y() + bar.get_height()/2,
        f"{width:,}",
        va="center"
    )

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "user_segmentation.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

#VIP 贡献率
# %%
segment_order = [
    "Low",
    "Regular",
    "High-value",
    "VIP"
]

segment_purchase = (
    user_rf
    .groupby("segment")["frequency"]
    .sum()
    .reindex(segment_order)
    .reset_index()
)

segment_purchase["purchase_share"] = (
    segment_purchase["frequency"]
    /
    segment_purchase["frequency"].sum()
)

print(segment_purchase)
#      segment  frequency  purchase_share
#0         Low     228546        0.113375
#1     Regular     871083        0.432119
#2  High-value     803217        0.398453
#3         VIP     112993        0.056053

# %%
