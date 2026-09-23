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

# ---------- CONFIG: parquet 路径 ----------
PARQUET_TASK_SUMMARY = "output_aggregate_further_data/03_dws_task_summary_1d.parquet"
PARQUET_TASK_LIFECYCLE = "output_aggregate_data/02_dwd_task_lifecycle.parquet"
PARQUET_EVENT_DETAIL = "output_aggregate_data/01_dwd_todo_event_detail.parquet"
PARQUET_EVENT_TYPE_SUM = "output_aggregate_further_data/04_dws_event_type_summary_1d.parquet"
PARQUET_DIM_TASK = "output_aggregate_data/03_dim_task.parquet"

# ---------- 读取函数 ----------
def try_read(path):
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()

DF_TASK_SUMMARY = try_read(PARQUET_TASK_SUMMARY)
DF_TASK_LIFECYCLE = try_read(PARQUET_TASK_LIFECYCLE)
DF_EVENT_DETAIL = try_read(PARQUET_EVENT_DETAIL)
DF_EVENT_TYPE_SUM = try_read(PARQUET_EVENT_TYPE_SUM)
DF_DIM_TASK = try_read(PARQUET_DIM_TASK)

# ---------- 小工具：生成 PNG 卡片（保持与其他模块一致的风格） ----------
# 新：KPI 原生 Card（替代 render_card_image 的图片卡片）
def _make_kpi_card(title, value, color="primary"):
    try:
        if isinstance(value, (int, float, np.integer, np.floating)):
            display = f"{value:,}"
        else:
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


# ---------- 视图构建函数 ----------
def build_overall_completion_cards(df_summary):
    total_created = int(df_summary["task_created_cnt"].sum()) if "task_created_cnt" in df_summary.columns else 0
    total_completed = int(df_summary["task_completed_cnt"].sum()) if "task_completed_cnt" in df_summary.columns else 0
    total_overdue = int(df_summary["overdue_cnt"].sum()) if "overdue_cnt" in df_summary.columns else 0
    avg_completion_rate = float(df_summary["completion_rate"].mean()) if "completion_rate" in df_summary.columns else 0.0
    avg_duration = float(df_summary["avg_complete_duration_seconds"].mean()) if "avg_complete_duration_seconds" in df_summary.columns else 0.0

    cards = [
        {"title": "总创建数", "value": total_created, "subtitle": ""},
        {"title": "总完成数", "value": total_completed, "subtitle": ""},
        {"title": "逾期数", "value": total_overdue, "subtitle": ""},
        {"title": "平均完成率", "value": f"{avg_completion_rate:.2%}", "subtitle": ""},
        {"title": "平均完成时长(s)", "value": int(avg_duration), "subtitle": ""}
    ]
    return cards



def build_completion_trend(df_summary):
    if df_summary.empty or "stat_date" not in df_summary.columns:
        return go.Figure()
    df = df_summary.copy()
    df["date"] = pd.to_datetime(df["stat_date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")

    # 强制数值转换（兼容字符串/百分号）
    def to_numeric_col(s):
        if s.dtype == object or s.dtype == "string":
            s2 = s.astype(str).str.strip()
            # 处理百分号字符串 "12%"
            pct_mask = s2.str.endswith("%")
            s_num = pd.to_numeric(s2.str.rstrip("%"), errors="coerce")
            s_num[pct_mask] = s_num[pct_mask] / 100.0
            return s_num
        return pd.to_numeric(s, errors="coerce")

    if "task_created_cnt" in df.columns:
        df["task_created_cnt_num"] = to_numeric_col(df["task_created_cnt"])
    if "task_completed_cnt" in df.columns:
        df["task_completed_cnt_num"] = to_numeric_col(df["task_completed_cnt"])
    if "completion_rate" in df.columns:
        df["completion_rate_num"] = to_numeric_col(df["completion_rate"])

    # 如果需要 secondary y（完成率），用 make_subplots 创建双 y 轴
    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if "task_created_cnt_num" in df.columns:
        y = df["task_created_cnt_num"].fillna(0)
        fig.add_trace(go.Scatter(x=df["date"], y=y, mode="lines+markers", name="创建数"), secondary_y=False)
    if "task_completed_cnt_num" in df.columns:
        y = df["task_completed_cnt_num"].fillna(0)
        fig.add_trace(go.Scatter(x=df["date"], y=y, mode="lines+markers", name="完成数"), secondary_y=False)
    if "completion_rate_num" in df.columns:
        y = df["completion_rate_num"].fillna(0)
        # 若 completion_rate 原是 0-1 比例，这里将其绘制为百分比轴显示
        fig.add_trace(go.Scatter(x=df["date"], y=y, mode="lines", name="完成率"), secondary_y=True)
        fig.update_yaxes(title_text="完成率", tickformat=".0%", secondary_y=True)

    fig.update_layout(title="任务创建/完成趋势", xaxis_title="日期", yaxis_title="数量", template="plotly_white", hovermode="x unified")
    return fig



def build_completion_gauge(df_summary):
    if df_summary.empty:
        return go.Figure()
    df = df_summary.copy()

    # 安全获取数值列，支持字符串、带% 的字符串、数值
    def to_numeric_safe(s):
        if s.dtype == object or s.dtype == "string":
            s2 = s.astype(str).str.strip()
            pct = s2.str.endswith("%")
            num = pd.to_numeric(s2.str.rstrip("%"), errors="coerce")
            num[pct] = num[pct] / 100.0
            return num
        return pd.to_numeric(s, errors="coerce")

    created_col = None
    completed_col = None
    if "task_created_cnt" in df.columns:
        created_col = "task_created_cnt"
    elif "task_created" in df.columns:
        created_col = "task_created"
    if "task_completed_cnt" in df.columns:
        completed_col = "task_completed_cnt"
    elif "task_completed" in df.columns:
        completed_col = "task_completed"

    total_created = 0
    total_completed = 0
    if created_col:
        total_created = int(to_numeric_safe(df[created_col]).sum(min_count=1) or 0)
    if completed_col:
        total_completed = int(to_numeric_safe(df[completed_col]).sum(min_count=1) or 0)

    # 计算按天累计比率（防除以 0）
    overall = (total_completed / max(1, total_created)) if total_created > 0 else 0.0
    display_value = overall * 100  # 转百分比用于仪表盘（0-100）

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=display_value,
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#2b8cbe"},
            "steps": [
                {"range": [0, 50], "color": "#fee0b6"},
                {"range": [50, 80], "color": "#fdae6b"},
                {"range": [80, 100], "color": "#2b8cbe"}
            ]
        },
        title={"text": "累计完成率（总完成 / 总创建）"}
    ))

    return fig



def build_priority_bars(df_lifecycle, df_dim_task=None, stacked=False):
    if df_lifecycle.empty:
        return go.Figure()
    df = df_lifecycle.copy()
    # 统一 priority 列名
    if "priority" not in df.columns and "task_priority" in df.columns:
        df["priority"] = df["task_priority"]
    df["priority"] = df["priority"].astype(str).fillna("未知")

    # 按优先级计算完成数/创建数/逾期数（若有）
    agg = df.groupby("priority").agg(
        total_tasks = ("task_id" if "task_id" in df.columns else "is_completed", "count"),
        completed = ("is_completed", lambda s: int((s==1).sum()) if s.dtype != 'O' else int(s.astype(bool).sum())) if "is_completed" in df.columns else ("task_id", "count"),
        overdue = ("is_overdue", lambda s: int((s==1).sum())) if "is_overdue" in df.columns else ("task_id", "count")
    ).reset_index()

    # 若 df_dim_task 提供更友好名称，可 merge
    if df_dim_task is not None and not df_dim_task.empty and "task_priority" in df_dim_task.columns:
        # 假设 df_dim_task 有 priority -> name 映射（如果存在）
        pass

    # 中文图例映射
    legend_map = {
        "total_tasks": "总任务数",
        "completed": "完成数",
        "overdue": "逾期数"
    }

    # 绘图
    if stacked:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=agg["priority"], y=agg["completed"], name=legend_map.get("completed", "完成数")))
        fig.add_trace(go.Bar(x=agg["priority"], y=agg["overdue"], name=legend_map.get("overdue", "逾期数")))
        fig.update_layout(barmode="stack", title="按优先级的任务完成/逾期分布", xaxis_title="优先级", yaxis_title="任务数", template="plotly_white")
        return fig
    else:
        dfm = agg.melt(id_vars="priority", value_vars=["total_tasks", "completed", "overdue"], var_name="metric", value_name="cnt")
        # 把 metric 列映射为中文，用作图例
        dfm["metric_label"] = dfm["metric"].map(legend_map).fillna(dfm["metric"])
        fig = px.bar(dfm, x="priority", y="cnt", color="metric_label", barmode="group", title="按优先级的任务统计（分组）")
        # 保持原有图例顺序（可选）
        return fig




def build_duration_hist_box(df_lifecycle):
    if df_lifecycle.empty or "complete_duration_seconds" not in df_lifecycle.columns:
        return go.Figure(), go.Figure()
    df = df_lifecycle.copy()
    df = df[df["complete_duration_seconds"].notna() & (df["complete_duration_seconds"] >= 0)]
    # 直方图
    hist = px.histogram(df, x="complete_duration_seconds", nbins=40, title="任务完成时长分布（秒）")
    # 箱线图（按优先级分箱）
    if "priority" in df.columns:
        box = px.box(df, x="priority", y="complete_duration_seconds", title="完成时长按优先级的箱线图")
    else:
        box = px.box(df, y="complete_duration_seconds", title="完成时长箱线图")
    return hist, box

def build_funnel(df_events, df_event_type_sum=None):
    # 使用事件类型序列构建创建 -> 完成/删除/延期 漏斗
    # 优先使用事件明细表：按 task_id 判断是否出现 create -> complete/delete/postpone
    if df_events.empty:
        return go.Figure()
    ev = df_events.copy()
    # 标准化 event_type 小写
    ev["event_type"] = ev["event_type"].astype(str).str.lower()
    # 过滤与任务相关的事件：假设 'create','complete','delete','postpone' 等关键字
    create_mask = ev["event_type"].str.contains("create", na=False)
    complete_mask = ev["event_type"].str.contains("complete", na=False)
    delete_mask = ev["event_type"].str.contains("delete", na=False)
    postpone_mask = ev["event_type"].str.contains("postpon", na=False) | ev["event_type"].str.contains("delay", na=False)

    total_created = ev[create_mask]["task_id"].nunique()
    total_completed = ev[complete_mask]["task_id"].nunique()
    total_deleted = ev[delete_mask]["task_id"].nunique()
    total_postponed = ev[postpone_mask]["task_id"].nunique()

    steps = ["创建", "完成", "删除", "延期"]
    values = [int(total_created), int(total_completed), int(total_deleted), int(total_postponed)]

    # 如果 event_type_sum 提供更精确的计数，也可参考
    fig = go.Figure(go.Funnel(
        y=steps,
        x=values,
        textinfo="value+percent initial"
    ))
    fig.update_layout(title="任务生命周期漏斗（创建 → 完成/删除/延期）")
    return fig

# ---------- 渲染主函数（返回 rows） ----------
def render_newold():
    # 构建所有图表和卡片
    cards = build_overall_completion_cards(DF_TASK_SUMMARY)
    fig_trend = build_completion_trend(DF_TASK_SUMMARY)
    fig_gauge = build_completion_gauge(DF_TASK_SUMMARY)
    fig_priority = build_priority_bars(DF_TASK_LIFECYCLE, DF_DIM_TASK, stacked=False)
    fig_priority_stack = build_priority_bars(DF_TASK_LIFECYCLE, DF_DIM_TASK, stacked=True)
    hist_duration, box_duration = build_duration_hist_box(DF_TASK_LIFECYCLE)
    fig_funnel = build_funnel(DF_EVENT_DETAIL, DF_EVENT_TYPE_SUM)

    # 数字卡片行
    card_cols = []
    # 可选：定义颜色序列或映射
    color_map = ["primary", "success", "danger", "info", "secondary"]
    for i, c in enumerate(cards):
        col = dbc.Col(
            _make_kpi_card(c["title"], c["value"], color=color_map[i % len(color_map)]),
            width=2
        )
        card_cols.append(col)

    # 如果列不足，补齐布局
    if len(card_cols) < 6:
        # 填充占位
        for _ in range(6 - len(card_cols)):
            card_cols.append(dbc.Col("", width=2))

    rows = [
        dbc.Row(card_cols, className="mb-3"),
        dbc.Row([dbc.Col(dcc.Graph(figure=fig_trend), width=8), dbc.Col(dcc.Graph(figure=fig_gauge), width=4)], className="mb-4"),
        dbc.Row([dbc.Col(dcc.Graph(figure=fig_priority), width=6), dbc.Col(dcc.Graph(figure=fig_priority_stack), width=6)], className="mb-4"),
        dbc.Row([dbc.Col(dcc.Graph(figure=hist_duration), width=6), dbc.Col(dcc.Graph(figure=box_duration), width=6)], className="mb-4"),
        dbc.Row([dbc.Col(dcc.Graph(figure=fig_funnel), width=12)], className="mb-4"),
    ]
    return rows