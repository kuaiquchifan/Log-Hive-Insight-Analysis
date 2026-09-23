# 09_viz_backend.py
import io
import base64
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
import seaborn as sns



# 数据文件（workspace 内）
FEATURE_PATH = "output_aggregate_further_data/09_dws_user_feature_usage_summary.parquet"
LIFECYCLE_PATH = "output_aggregate_data/02_dwd_task_lifecycle.parquet"
USER_PATH = "output_data/01_dim_user.parquet"
BEHAVIOR_PATH = "output_aggregate_further_data/02_dws_user_behavior_summary.parquet"

def _safe_read(path):
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()

# 将 has_reminder/has_subtask/due_date 标准化为 0/1（安全处理 None/NaN/字符串）
def safe_bool_to_int(s):
    s = s.copy()
    # 首先将常见布尔型、数值型、字符串型统一转换为 numeric/boolean
    s = pd.to_numeric(s, errors="coerce")  # 无法转换的变为 NaN
    # 非空且非零视为 1
    s = s.fillna(0).apply(lambda x: 1 if x else 0).astype(int)
    return s


def _make_kpi_card(title, value, color="primary"):
    # 如果是数字则格式化，否则直接显示（例如 "12.3%")
    try:
        if isinstance(value, (int, float, np.integer, np.floating)):
            display = f"{value:,}"
        else:
            # 尝试把可能是带 % 的字符串安全地作为显示文本
            display = str(value)
    except Exception:
        display = str(value)
    return dbc.Card(
        dbc.CardBody([
            html.Div(title, className="text-muted"),
            html.H4(display, className="mt-2")
        ]),
        color=color, inverse=False, className="m-1"
    )

def render_export():
    # 1) 读取数据
    feat = _safe_read(FEATURE_PATH)
    lifecycle = _safe_read(LIFECYCLE_PATH)
    users = _safe_read(USER_PATH)
    behavior = _safe_read(BEHAVIOR_PATH)

    # 如果数据为空，返回占位
    if feat.empty:
        return [dbc.Row([dbc.Col(html.H4("功能使用深度分析：未找到数据文件或数据为空"), width=12)])]

    # 2) 功能使用趋势（按 stat_date 聚合）
    feat["stat_date"] = pd.to_datetime(feat["stat_date"])
    trend = feat.sort_values("stat_date").groupby("stat_date", as_index=False)[
        ["remind_feature_usage_rate", "subtask_usage_rate", "due_date_setting_rate"]
    ].mean()
    trend_long = trend.melt(id_vars="stat_date", var_name="feature", value_name="rate")

    trend_fig = px.line(trend_long, x="stat_date", y="rate", color="feature",
                        labels={"rate": "使用率", "stat_date": "日期", "feature": "功能"},
                        title="功能使用率趋势（按日平均）")
    trend_fig.update_layout(margin=dict(l=10,r=10,t=40,b=10))

    # KPI 数字卡片：取最近日期值
    latest = trend.iloc[-1] if not trend.empty else None
    kpis = []
    if latest is not None:
        kpis = [
            _make_kpi_card("提醒使用率", f"{latest.remind_feature_usage_rate:.1%}", color="info"),
            _make_kpi_card("子任务使用率", f"{latest.subtask_usage_rate:.1%}", color="success"),
            _make_kpi_card("截止日期设置率", f"{latest.due_date_setting_rate:.1%}", color="warning"),
        ]

    # 3) 功能使用对完成率影响（按用户或任务聚合）
    # 使用 lifecycle 与 feat：标注任务是否具有功能
    if not lifecycle.empty:
        # 将 has_reminder/has_subtask/due_date 标准化到布尔列
        lifecycle["has_reminder"] = safe_bool_to_int(lifecycle.get("has_reminder", 0))
        lifecycle["has_subtask"] = safe_bool_to_int(lifecycle.get("has_subtask", 0))
        # due_date 为空则视为无截止日期
        lifecycle["has_due_date"] = (~lifecycle["due_date"].isna()).astype(int)

        # 计算分组完成率（功能有 vs 无）
        def grouped_completion(col, label):
            g = lifecycle.groupby(col).agg(
                tasks_total=("task_id", "count"),
                tasks_completed=("is_completed", "sum")
            ).reset_index()
            g["completion_rate"] = g["tasks_completed"] / g["tasks_total"]
            g[col] = g[col].map({0: "无 "+label, 1: "有 "+label})
            return g
        g_remind = grouped_completion("has_reminder", "提醒")
        g_subtask = grouped_completion("has_subtask", "子任务")
        g_due = grouped_completion("has_due_date", "截止日期")

        # 合并用于并排柱状图显示
        def make_bar_df(gdf, feature_name, key_name="has_feature"):
            gdf = gdf.copy()
            first_col = gdf.columns[0]
            gdf = gdf.rename(columns={first_col: key_name})
            gdf[key_name] = gdf[key_name].astype(str)  # 确保为字符串标签
            gdf["feature"] = feature_name
            return gdf[["feature", key_name, "completion_rate", "tasks_total"]]

        bar_df = pd.concat([
            make_bar_df(g_remind, "提醒"),
            make_bar_df(g_subtask, "子任务"),
            make_bar_df(g_due, "截止日期")
        ], ignore_index=True)

        bar_fig = px.bar(bar_df, x="has_feature", y="completion_rate", color="feature", barmode="group",
                        labels={"has_feature": "是否有功能", "completion_rate": "完成率"},
                        title="有功能 vs 无功能：任务完成率对比")
        bar_fig.update_yaxes(tickformat=".0%")

    else:
        bar_fig = go.Figure()
        bar_fig.update_layout(title="任务生命周期数据缺失，无法计算功能对完成率影响")

    # 4) 不同用户分群的功能使用差异
    # DEBUG: 检查列存在性与简单统计
    print("feat columns:", feat.columns.tolist())
    print("users columns:", users.columns.tolist())
    print("behavior columns:", behavior.columns.tolist())

    # 1) 构造 user_feat（并确保 user_id 为字符串以统一类型）
    if "user_id" in lifecycle.columns:
        user_feat = lifecycle.groupby("user_id").agg(
            remind_rate=("has_reminder", "mean"),
            subtask_rate=("has_subtask", "mean"),
            due_rate=("has_due_date", "mean")
        ).reset_index()
        user_feat["user_id"] = user_feat["user_id"].astype(str)
    else:
        user_feat = pd.DataFrame()

    # 2) 仅在必要列存在时继续
    if not users.empty and not behavior.empty and not user_feat.empty:
        users_small = users[["user_id", "user_group", "user_level", "user_type"]].drop_duplicates()
        users_small["user_id"] = users_small["user_id"].astype(str)
        behavior_small = behavior[["user_id", "completion_rate"]].drop_duplicates()
        behavior_small["user_id"] = behavior_small["user_id"].astype(str)

        # debug: 打印样本与行数
        print("user_feat rows:", len(user_feat))
        print("users_small rows:", len(users_small))
        print("behavior_small rows:", len(behavior_small))
        print("user_group unique count:", users_small["user_group"].nunique() if "user_group" in users_small else "missing")

        merged = user_feat.merge(users_small, on="user_id", how="left").merge(behavior_small, on="user_id", how="left")

        # debug: 合并后空值程度
        print("merged rows:", len(merged))
        print("merged user_group null ratio:", merged["user_group"].isna().mean())
        print("merged completion_rate null ratio:", merged["completion_rate"].isna().mean())

        # 用 fillna 或者丢弃没有分群信息的行（根据业务决策）
        merged = merged.dropna(subset=["user_group"])  # 如果想保留所有则改为 fillna("unknown")
        merged["completion_rate"] = merged["completion_rate"].fillna(0)

        # 计算每个 user_group 的平均功能使用率
        group_cols = ["user_group"]
        group_summary = merged.groupby(group_cols).agg(
            remind_rate=("remind_rate", "mean"),
            subtask_rate=("subtask_rate", "mean"),
            due_rate=("due_rate", "mean"),
            completion_rate=("completion_rate", "mean")
        ).reset_index().fillna(0)

        # 分组条形图
        group_long = group_summary.melt(id_vars="user_group", value_vars=["remind_rate","subtask_rate","due_rate"],
                                        var_name="feature", value_name="rate")
        group_fig = px.bar(group_long, x="user_group", y="rate", color="feature", barmode="group",
                        labels={"user_group":"用户分群","rate":"平均使用率"}, title="不同用户分群的功能使用差异")

        # 热力图：不要转置（用直观的行=用户分群，列=功能）
        heat_df = group_summary.set_index("user_group")[["remind_rate","subtask_rate","due_rate"]]
        heat_fig = px.imshow(heat_df, labels=dict(x="功能", y="用户分群", color="使用率"),
                            x=list(heat_df.columns), y=list(heat_df.index), title="分群-功能使用率热力图")
        heat_fig.update_coloraxes(colorbar_tickformat=".0%")
    else:
        group_fig = go.Figure()
        group_fig.update_layout(title="缺少用户或行为数据，无法生成分群对比")
        heat_fig = go.Figure()
        heat_fig.update_layout(title="缺少用户或行为数据，无法生成热力图")

    # 布局：KPI 行、趋势图行、功能影响行、分群对比行
    rows = []

    # KPI 行
    if kpis:
        rows.append(dbc.Row([dbc.Col(card, width=4) for card in kpis], className="mb-3"))

    # 趋势图
    rows.append(dbc.Row([dbc.Col(dcc.Graph(figure=trend_fig), width=12)], className="mb-3"))

    # 功能对完成率
    rows.append(dbc.Row([dbc.Col(dcc.Graph(figure=bar_fig), width=12)], className="mb-3"))

    # 分群对比 + 热力图
    rows.append(dbc.Row([
        dbc.Col(dcc.Graph(figure=group_fig), width=6),
        dbc.Col(dcc.Graph(figure=heat_fig), width=6),
    ], className="mb-3"))

    # debug:查看三列的唯一值/分布
    print("has_reminder unique:", lifecycle.get("has_reminder").unique() if "has_reminder" in lifecycle else "missing")
    print("has_reminder value_counts:\n", lifecycle.get("has_reminder").value_counts(dropna=False).head(10))

    print("has_subtask unique:", lifecycle.get("has_subtask").unique() if "has_subtask" in lifecycle else "missing")
    print("has_subtask value_counts:\n", lifecycle.get("has_subtask").value_counts(dropna=False).head(10))

    print("due_date null ratio:", lifecycle["due_date"].isna().mean() if "due_date" in lifecycle else "missing")
    print("has_due_date unique after conversion:", lifecycle["has_due_date"].value_counts(dropna=False).to_dict())


    return rows