from pathlib import Path
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

# 设置路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_OUTPUT_DIR = PROJECT_ROOT / "sql"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures" / "chapter1"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

#print("Current working directory:", Path.cwd())
#print("Project root:", PROJECT_ROOT)
#print("Raw data directory:", RAW_DATA_DIR)

#文件读取
daily_summary = pd.read_csv(
    SQL_OUTPUT_DIR / "daily_behavior_count.csv"
)

hourly_summary = pd.read_csv(
    SQL_OUTPUT_DIR / "hourly_behavior_count.csv"
)

hourly_active_users = pd.read_csv(
    SQL_OUTPUT_DIR / "hourly_active_users.csv"
)

daily_active_users = pd.read_csv(
    SQL_OUTPUT_DIR / "daily_active_users.csv"
)

#数据概览
#print("daily_summary shape:", daily_summary.shape)
#print("hourly_summary shape:", hourly_summary.shape)
#print("hourly_active_users shape:", hourly_active_users.shape)
#print("daily_active_users shape:", daily_active_users.shape)
#print(daily_summary.head())
#print()
#print(hourly_summary.head())
#print()
#print(hourly_active_users.head())
#print()
#print(daily_active_users.head())


#Q1:用户哪一天最活跃？（折线图）
# 转换长表
daily_behavior = (
    daily_summary
    .pivot(
        index="date",
        columns="behavior_type",
        values="cnt"
    )
    .reset_index()
)

daily_user = (
    daily_active_users
    .pivot(
        index="date",
        columns="behavior_type",
        values="active_user"
    )
    .reset_index()
)

hourly_behavior = (
    hourly_summary
    .pivot(
        index=["date", "hour"],
        columns="behavior_type",
        values="behavior_count"
    )
    .reset_index()
)

hourly_user = (
    hourly_active_users
    .pivot(
        index=["date", "hour"],
        columns="behavior_type",
        values="active_user"
    )
    .reset_index()
)


#表格一览
#print(daily_behavior.head())
#print(daily_user.head())

#print(daily_behavior.describe())
#print(daily_user.describe())

#画图
daily_behavior["date"] = pd.to_datetime(daily_behavior["date"])
daily_behavior = daily_behavior.sort_values("date")

daily_user["date"] = pd.to_datetime(daily_user["date"])
daily_user = daily_user.sort_values("date")

hourly_behavior["datetime"] = pd.to_datetime(
    hourly_behavior["date"]
) + pd.to_timedelta(hourly_behavior["hour"], unit="h")

hourly_user["datetime"] = pd.to_datetime(
    hourly_user["date"]
) + pd.to_timedelta(hourly_user["hour"], unit="h")

#Daily Page View Trend
plt.figure(figsize=(10, 5))

plt.plot(
    daily_behavior["date"],
    daily_behavior["pv"],
    marker="o",
    linewidth=2
)

plt.title("Daily Page View Trend")
plt.xlabel("Date")
plt.ylabel("Page Views")

plt.xticks(rotation=45)
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(
    FIGURES_DIR / "Fig1_daily_page_view_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Daily Purchase-related Behaviors
plt.figure(figsize=(10, 5))

for behavior in ["buy", "cart", "fav"]:
    plt.plot(
        daily_behavior["date"],
        daily_behavior[behavior],
        marker="o",
        linewidth=2,
        label=behavior.capitalize()
    )

plt.title("Daily Purchase-related Behaviors")
plt.xlabel("Date")
plt.ylabel("Behavior Count")

plt.legend()
plt.grid(alpha=0.3)
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig(
    FIGURES_DIR / "Fig2_daily_purchase_behaviors.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Daily Active Users
plt.figure(figsize=(10, 5), dpi=150)

plt.plot(
    daily_user["date"],
    daily_user["pv"],
    marker="o",
    linewidth=2
)

plt.title("Daily Active Users (Page View)")
plt.xlabel("Date")
plt.ylabel("Active Users")

plt.xticks(rotation=45)
plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig3_Daily_Active_Users.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Hourly Page View Trend
plt.figure(figsize=(12, 5), dpi=150)

plt.plot(
    hourly_behavior["datetime"],
    hourly_behavior["pv"],
    linewidth=1.8
)

plt.title("Hourly Page View Trend")
plt.xlabel("Time")
plt.ylabel("Page Views")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig4_Hourly_Page_View_Trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Hourly Purchase-related Behaviors
plt.figure(figsize=(12, 5), dpi=150)

for behavior in ["buy", "cart", "fav"]:
    plt.plot(
        hourly_behavior["datetime"],
        hourly_behavior[behavior],
        linewidth=1.5,
        label=behavior.capitalize()
    )

plt.title("Hourly Purchase-related Behaviors")
plt.xlabel("Time")
plt.ylabel("Behavior Count")

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig5_Hourly_Purchase_Related_Trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#hourly Active Users(PV)
plt.figure(figsize=(12, 5), dpi=150)

plt.plot(
    hourly_user["datetime"],
    hourly_user["pv"],
    linewidth=1.8
)

plt.title("Hourly Active Users (Page View)")
plt.xlabel("Time")
plt.ylabel("Active Users")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig6_Hourly_Active_Users.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Hourly Purchase-related Active Users
plt.figure(figsize=(12, 5), dpi=150)

for behavior in ["buy", "cart", "fav"]:
    plt.plot(
        hourly_user["datetime"],
        hourly_user[behavior],
        linewidth=1.5,
        label=behavior.capitalize()
    )

plt.title("Hourly Purchase-related Active Users")
plt.xlabel("Time")
plt.ylabel("Active Users")

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig7_Hourly_Purchase_Related_Active_Users.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Q2：一天中什么时间最活跃？(Heatmap)
#数据准备
pv_heatmap = (
    hourly_behavior
    .pivot(
        index="date",
        columns="hour",
        values="pv"
    )
)

buy_heatmap = (
    hourly_behavior
    .pivot(
        index="date",
        columns="hour",
        values="buy"
    )
)

pv_user_heatmap = (
    hourly_user
    .pivot(
        index="date",
        columns="hour",
        values="pv"
    )
)

buy_user_heatmap = (
    hourly_user
    .pivot(
        index="date",
        columns="hour",
        values="buy"
    )
)

#画图-Hourly_Page_View_Heatmap
plt.figure(figsize=(12, 4), dpi=150)

plt.imshow(
    pv_heatmap,
    aspect="auto",
    cmap="YlOrRd"
)

plt.colorbar(label="Page Views")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(pv_heatmap.index)),
    pv_heatmap.index
)

plt.xlabel("Hour of Day")
plt.ylabel("Date")
plt.title("Hourly Page View Heatmap")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig4_Hourly_Page_View_Heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#画图-Hourly_Buy_Heatmap
plt.figure(figsize=(12, 4), dpi=150)

plt.imshow(
    buy_heatmap,
    aspect="auto",
    cmap="YlOrRd"
)

plt.colorbar(label="Buy Count")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(buy_heatmap.index)),
    buy_heatmap.index
)

plt.xlabel("Hour of Day")
plt.ylabel("Date")
plt.title("Hourly Buy Heatmap")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig5.1_Hourly_Buy_Heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#画图-Hourly_Page_View_User_Heatmap
plt.figure(figsize=(12, 4), dpi=150)

plt.imshow(
    pv_user_heatmap,
    aspect="auto",
    cmap="YlOrRd"
)

plt.colorbar(label="Page Views")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(pv_user_heatmap.index)),
    pv_user_heatmap.index
)

plt.xlabel("Hour of Day")
plt.ylabel("Date")
plt.title("Hourly Page View Heatmap (Active Users)")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig6_Hourly_Page_View_User_Heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#画图-Hourly_Buy_User_Heatmap
plt.figure(figsize=(12, 4), dpi=150)

plt.imshow(
    buy_user_heatmap,
    aspect="auto",
    cmap="YlOrRd"
)

plt.colorbar(label="Buy Count")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(buy_user_heatmap.index)),
    buy_heatmap.index
)

plt.xlabel("Hour of Day")
plt.ylabel("Date")
plt.title("Hourly Buy Heatmap (Active Users)")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "Fig7.1_Hourly_Buy_User_Heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Q3:活跃是因为更多用户，还是因为用户更活跃？
#指标计算：behavior_type/active_user
daily_engagement = pd.DataFrame({
    "date": daily_behavior["date"]
})

for behavior in ["pv", "cart", "fav", "buy"]:
    daily_engagement[behavior] = (
        daily_behavior[behavior]
        / daily_user[behavior]
    )

#print(daily_engagement.head())

#绘图
#PV engagement trend
plt.figure(figsize=(10, 5), dpi=150)

plt.plot(
    daily_engagement["date"],
    daily_engagement["pv"],
    marker="o",
    linewidth=2
)

plt.title("Average Page Views per Active User")
plt.xlabel("Date")
plt.ylabel("PV per User")

plt.grid(alpha=0.3)

plt.savefig(
    FIGURES_DIR / "Fig8_Average_Page_Views_Per_User.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Other engagement trends
plt.figure(figsize=(10, 5), dpi=150)

for behavior in ["cart", "fav", "buy"]:
    plt.plot(
        daily_engagement["date"],
        daily_engagement[behavior],
        marker="o",
        linewidth=2,
        label=behavior.capitalize()
    )

plt.title("Average Purchase-related Behaviors per Active User")
plt.xlabel("Date")
plt.ylabel("Actions per User")

plt.legend()
plt.grid(alpha=0.3)

plt.savefig(
    FIGURES_DIR / "Fig9_Average_Purchase_Behaviors_Per_User.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()