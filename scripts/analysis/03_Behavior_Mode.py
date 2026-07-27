from pathlib import Path
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_OUTPUT_DIR = PROJECT_ROOT / "sql"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures" / "chapter3"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

category_summary = pd.read_csv(
    SQL_OUTPUT_DIR / "category_summary.csv"
)

#print(category_summary.head())

#计算指标
category_summary["fav_rate"] = np.where(
    category_summary["pv"] > 0,
    category_summary["fav"] / category_summary["pv"],
    np.nan
)

category_summary["cart_rate"] = np.where(
    category_summary["pv"] > 0,
    category_summary["cart"] / category_summary["pv"],
    np.nan
)

category_summary["buy_rate"] = np.where(
    category_summary["pv"] > 0,
    category_summary["buy"] / category_summary["pv"],
    np.nan
)

category_summary["cart_to_buy_rate"] = np.where(
    category_summary["cart"] > 0,
    category_summary["buy"] / category_summary["cart"],
    np.nan
)

pv_threshold = category_summary["pv"].quantile(0.90)

category_behavior = category_summary[
    category_summary["pv"] >= pv_threshold
].copy()

#print("PV threshold:", pv_threshold)
#print(category_behavior.shape)

behavior_metrics = [
    "pv",
    "fav",
    "cart",
    "buy",
    "fav_rate",
    "cart_rate",
    "buy_rate",
    "cart_to_buy_rate"
]

#print(category_behavior[behavior_metrics].describe())

top10_fav_rate = (
    category_behavior
    .sort_values("fav_rate", ascending=False)
    .head(10)
)

top10_cart_rate = (
    category_behavior
    .sort_values("cart_rate", ascending=False)
    .head(10)
)

top10_buy_rate = (
    category_behavior
    .sort_values("buy_rate", ascending=False)
    .head(10)
)

top10_cart_to_buy = (
    category_behavior
    .sort_values("cart_to_buy_rate", ascending=False)
    .head(10)
)

behavior_compare = category_behavior[
    [
        "category_id",
        "fav_rate",
        "cart_rate",
        "buy_rate"
    ]
]

#print(behavior_compare.head())

top_buy = top10_buy_rate["category_id"]

compare_df = (
    category_behavior[
        category_behavior["category_id"].isin(top_buy)
    ]
    .set_index("category_id")
)

compare_df[
    ["fav_rate","cart_rate","buy_rate"]
].plot(
    kind="bar",
    figsize=(10,6)
)

plt.ylabel("Rate")
plt.title("Behavior Comparison Across Categories")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "behavior_comparison.png"
)

plt.close()


# core cat
core_categories=[1320293, 4756105, 982926, 4801426, 4145813]

core_behavior = (
    category_summary[
        category_summary["category_id"].isin(core_categories)
    ]
    .copy()
)

core_behavior_plot = (
    core_behavior
    .set_index("category_id")[
        ["fav_rate", "cart_rate", "buy_rate"]
    ]
)

core_behavior_plot.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.ylabel("Rate")
plt.xlabel("Category ID")
plt.title("Behavior Rates of Core Categories")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "core_category_behavior.png"
)

plt.close()

#behavior composition
behavior_order = ["pv", "fav", "cart", "buy"]

composition = core_behavior.set_index("category_id")[behavior_order].copy()

composition = composition.div(
    composition.sum(axis=1),
    axis=0
)
core_categories = core_behavior["category_id"]

composition = composition.loc[core_categories]

#绘图
behavior_order = [
    "pv",
    "fav",
    "cart",
    "buy"
]

bottom = np.zeros(len(composition))

plt.figure(figsize=(10, 6))

for behavior in behavior_order:
    plt.bar(
        composition.index.astype(str),
        composition[behavior],
        bottom=bottom,
        label=behavior
    )

    bottom += composition[behavior]

    plt.ylabel("Proportion")
plt.xlabel("Category ID")
plt.title("Behavior Composition of Core Categories")

plt.legend(title="Behavior")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "behavior_composition.png"
)

plt.close()
