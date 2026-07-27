from pathlib import Path
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_OUTPUT_DIR = PROJECT_ROOT / "sql"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures" / "chapter2"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

#读取数据
cat_item_df = pd.read_csv(SQL_OUTPUT_DIR / "cat_item_df.csv")

#print(cat_item_df.shape)
#print(cat_item_df.head())

# 重命名计数列
cat_item_df = cat_item_df.rename(
    columns={"count(behavior_type)": "behavior_count"}
)

# 转换长表
cat_item_wide = (
    cat_item_df
    .pivot_table(
        index=["category_id", "item_id"],
        columns="behavior_type",
        values="behavior_count",
        aggfunc="sum",
        fill_value=0
    )
    .reset_index()
)

cat_item_wide.columns.name = None

for col in ["pv", "fav", "cart", "buy"]:
    if col not in cat_item_wide.columns:
        cat_item_wide[col] = 0

# 调整列顺序
cat_item_wide = cat_item_wide[
    ["category_id", "item_id", "pv", "fav", "cart", "buy"]
]

#print(cat_item_wide.shape) 
#print(cat_item_wide.head())

# 汇总到cat层级
category_summary = (
    cat_item_wide
    .groupby("category_id", as_index=False)
    .agg(
        item_count=("item_id", "nunique"),
        pv=("pv", "sum"),
        fav=("fav", "sum"),
        cart=("cart", "sum"),
        buy=("buy", "sum")
    )
)

# 计算转化率
category_summary["conversion_rate"] = (
    category_summary["buy"] / category_summary["pv"]
)

#print(category_summary.shape)
#print(category_summary.head())

#保存中间表格
#cat_item_wide.to_csv(
#    PROCESSED_DATA_DIR / "cat_item_behavior_wide.csv",
#    index=False
#)

#category_summary.to_csv(
#    PROCESSED_DATA_DIR / "category_summary.csv",
#    index=False
#)

#top 10 pv cat
top10_pv = (
    category_summary
    .sort_values("pv",ascending = False)
    .head(10)
)

#print(top10_pv)

#画图
plt.figure(figsize=(10,6))

plt.bar(
    top10_pv["category_id"].astype(str),
    top10_pv["pv"]
)

plt.title("Top 10 Categories by Page Views")
plt.xlabel("Category ID")
plt.ylabel("PV")

plt.xticks(rotation = 45)
plt.tight_layout()
plt.savefig(FIGURES_DIR/"top10_category_pv.png")
plt.close()

#top10 buy cat
top10_buy = (
    category_summary
    .sort_values("buy",ascending = False)
    .head(10)
)

#print(top10_buy)

#top10_buy.to_csv(
#    PROCESSED_DATA_DIR / "top10_category_buy.csv",
#    index=False
#)

#画图
plt.figure(figsize=(10,6))

plt.bar(
    top10_buy["category_id"].astype(str),
    top10_buy["buy"]
)

plt.title("Top 10 Categories by Buys")
plt.xlabel("Category ID")
plt.ylabel("Buy")

plt.xticks(rotation = 45)
plt.tight_layout()
plt.savefig(FIGURES_DIR/"top10_category_buy.png")
plt.close()

#Top10 转化率 需要过滤
pv_threshold = category_summary["pv"].quantile(0.90)

#print(f"PV Threshold: {pv_threshold:.0f}")

filtered_category = category_summary[
    category_summary["pv"] >= pv_threshold
].copy()

top10_conversion = (
    filtered_category
    .sort_values("conversion_rate", ascending=False)
    .head(10)
)

#top10_conversion.to_csv(
#    PROCESSED_DATA_DIR / "top10_category_conversion.csv",
#    index=False
#)
#print(top10_conversion[["category_id", "pv", "buy", "conversion_rate"]])

#确定研究对象
pv_set = set(top10_pv["category_id"])
buy_set = set(top10_buy["category_id"])
conversion_set = set(top10_conversion["category_id"])

#print("PV ∩ Buy")
#print(pv_set & buy_set)
#{1320293, 4756105, 982926, 4801426, 4145813}

#print("PV ∩ Conversion")
#print(pv_set & conversion_set)

#print("Buy ∩ Conversion")
#print(buy_set & conversion_set)

#print("All Three")
#print(pv_set & buy_set & conversion_set)

core_categories = list(pv_set & buy_set)

#根据核心分析 {1320293, 4756105, 982926, 4801426, 4145813}
core_item_df = cat_item_wide[
    cat_item_wide["category_id"].isin(core_categories)
].copy()

#print(core_item_df.shape)
#print(core_item_df.head())

#每个cat的top20 pv
top20_item_pv = (
    core_item_df
    .sort_values(
        ["category_id", "pv"],
        ascending=[True, False]
    )
    .groupby("category_id")
    .head(20)
)

#top20_item_pv.to_csv(
#    PROCESSED_DATA_DIR / "top20_item_pv.csv",
#    index=False
#)

#每个Cat的top20 buy
top20_item_buy = (
    core_item_df
    .sort_values(
        ["category_id", "buy"],
        ascending=[True, False]
    )
    .groupby("category_id")
    .head(20)
)

#top20_item_buy.to_csv(
#    PROCESSED_DATA_DIR / "top20_item_buy.csv",
#    index=False
#)

#看是否为某一item驱动型
category_item_summary = (
    top20_item_pv
    .groupby("category_id")
    .agg(
        top20_pv=("pv", "sum"),
        max_pv=("pv", "max"),
        mean_pv=("pv", "mean")
    )
)

category_item_summary["top1_share"] = (
    category_item_summary["max_pv"] /
    category_item_summary["top20_pv"]
)

#print(category_item_summary)

#category_item_summary.to_csv(
#    PROCESSED_DATA_DIR / "category_item_summary.csv",
#    index=False
#)

#按照核心cat里的item分析
item_count = (
    core_item_df
    .groupby("category_id")
    .agg(
        item_num=("item_id", "nunique")
    )
)

#pv
for category in core_categories:

    temp = (
        top20_item_pv[
            top20_item_pv["category_id"] == category
        ]
        .sort_values("pv", ascending=False)
    )

    plt.figure(figsize=(10,5))

    plt.bar(
        temp["item_id"].astype(str),
        temp["pv"]
    )

    plt.title(f"Top20 Items by PV - Category {category}")
    plt.xlabel("Item ID")
    plt.ylabel("PV")

    plt.xticks(rotation=90)

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / f"category_{category}_top20_pv.png"
    )

    plt.close()

#buy
for category in core_categories:

    temp = (
        top20_item_buy[
            top20_item_buy["category_id"] == category
        ]
        .sort_values("buy", ascending=False)
    )

    plt.figure(figsize=(10,5))

    plt.bar(
        temp["item_id"].astype(str),
        temp["buy"]
    )

    plt.title(f"Top20 Items by Buy - Category {category}")
    plt.xlabel("Item ID")
    plt.ylabel("Buy")

    plt.xticks(rotation=90)

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / f"category_{category}_top20_buy.png"
    )

    plt.close()

#爆款分析
item_concentration = (
    core_item_df
    .groupby("category_id")
    .agg(
        total_pv=("pv", "sum"),
        max_pv=("pv", "max"),
        total_buy=("buy", "sum"),
        max_buy=("buy", "max")
    )
)

item_concentration["pv_top1_share"] = (
    item_concentration["max_pv"] /
    item_concentration["total_pv"]
)

item_concentration["buy_top1_share"] = (
    item_concentration["max_buy"] /
    item_concentration["total_buy"]
)

item_concentration.to_csv(
    PROCESSED_DATA_DIR / "item_concentration.csv",
    index=False
)