# app.py
import io
import base64
from datetime import timedelta

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- CONFIG ----------
PARQUET_ACTIVE = "output_aggregate_further_data/01_dws_user_active_1d.parquet"
PARQUET_DATE = "output_data/02_dim_date.parquet"
PARQUET_NEWOLD = "output_aggregate_further_data/07_dws_new_old_user_summary.parquet"
# ---------- HELPERS ----------
def read_parquets():
    df_active = pd.read_parquet(PARQUET_ACTIVE)
    df_date = pd.read_parquet(PARQUET_DATE)
    df_newold = pd.read_parquet(PARQUET_NEWOLD)
    return df_active, df_date, df_newold

def to_date_series(s):
    # 支持 YYYYMMDD 整数或字符串，或 ISO 字符串
    if pd.api.types.is_integer_dtype(s) or pd.api.types.is_float_dtype(s):
        return pd.to_datetime(s.astype(int).astype(str), format="%Y%m%d", errors="coerce")
    return pd.to_datetime(s, errors="coerce")

def to_date_col(df, col="date"):
    if df[col].dtype == "int64" or df[col].dtype == "float64":
        # 尝试按 YYYYMMDD 整数转换
        try:
            return pd.to_datetime(df[col].astype(int).astype(str), format="%Y%m%d")
        except Exception:
            return pd.to_datetime(df[col])
    return pd.to_datetime(df[col])

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf8')
    return "data:image/png;base64," + img_b64

def render_card_image(title, value, subtitle=None, width=320, height=120):
    sns.set_style("whitegrid")
    plt.figure(figsize=(width/100, height/100))
    plt.axis('off')
    # 背景色与文本布局
    plt.gca().add_patch(plt.Rectangle((0,0),1,1, color="#0f1724"))
    plt.text(0.05, 0.65, title, fontsize=11, color="#cbd5e1", transform=plt.gca().transAxes)
    plt.text(0.05, 0.24, f"{value:,}", fontsize=28, color="white", weight="bold", transform=plt.gca().transAxes)
    if subtitle:
        plt.text(0.05, 0.05, subtitle, fontsize=9, color="#94a3b8", transform=plt.gca().transAxes)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    plt.close()
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf8')

# ---------- BUILD FIGURES ----------
def build_active_figures(df_active, df_date):
    # df_active: user-level rows with 'user_id' and 'stat_date'
    df = df_active.copy()
    if 'stat_date' not in df.columns:
        raise KeyError("活跃表缺少 stat_date 列")
    df['date'] = to_date_series(df['stat_date'])
    df = df.dropna(subset=['date'])
    # 计算 DAU：每天去重 user_id 数
    dau = df.groupby('date')['user_id'].nunique().reset_index().rename(columns={'user_id':'dau'})
    dau = dau.sort_values('date')
    # 计算 WAU/MAU：近似方法 — 对于每个日期，计算过去7/30天内去重用户数
    dau.set_index('date', inplace=True)
    # 为了计算窗口内去重用户数，需要用 rolling on daily sets — 先构造每日用户集合
    daily_users = df.groupby('date')['user_id'].apply(lambda s: set(s.tolist()))
    # 构造 dataframe with dates in range
    all_dates = pd.date_range(dau.index.min(), dau.index.max(), freq='D')
    res = pd.DataFrame(index=all_dates)
    res = res.join(dau['dau'])
    # helper to compute unique count over last N days
    def unique_count_over_window(end_date, days):
        window = pd.date_range(end_date - pd.Timedelta(days=days-1), end_date, freq='D')
        users = set()
        for d in window:
            if d in daily_users.index:
                users |= daily_users.loc[d]
        return len(users)
    # compute WAU/MAU for each date (may be slower on long ranges)
    res['wau'] = [unique_count_over_window(d.date(), 7) for d in res.index]
    res['mau'] = [unique_count_over_window(d.date(), 30) for d in res.index]
    res = res.reset_index().rename(columns={'index':'date'})
    # 绘图
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=res['date'], y=res['dau'], mode='lines+markers', name='DAU'))
    fig_line.add_trace(go.Scatter(x=res['date'], y=res['wau'], mode='lines+markers', name='WAU'))
    fig_line.add_trace(go.Scatter(x=res['date'], y=res['mau'], mode='lines+markers', name='MAU'))
    fig_line.update_layout(title="用户活跃趋势", xaxis_title="日期", yaxis_title="用户数", hovermode="x unified", template="plotly_white")
    # 数字卡：取最后一天数据
    last_date = res['date'].max()
    last_row = res[res['date']==last_date].iloc[0]
    cards = {
        'DAU': {'today': int(last_row['dau']), '7d_avg': int(res['dau'].tail(7).mean()), '30d_avg': int(res['dau'].tail(30).mean())},
        'WAU': {'today': int(last_row['wau']), '7d_avg': int(res['wau'].tail(7).mean()), '30d_avg': int(res['wau'].tail(30).mean())},
        'MAU': {'today': int(last_row['mau']), '7d_avg': int(res['mau'].tail(7).mean()), '30d_avg': int(res['mau'].tail(30).mean())},
    }
    return fig_line, cards, last_date



def build_newold_figures(df_newold):
    # df_newold 包含 stat_date, new_user_cnt, old_user_cnt
    df = df_newold.copy()
    if 'stat_date' not in df.columns:
        raise KeyError("新老用户表缺少 stat_date 列")
    df['date'] = to_date_series(df['stat_date'])
    df = df.sort_values('date')
    # 堆叠柱状图
    fig_stack = go.Figure()
    if 'new_user_cnt' in df.columns and 'old_user_cnt' in df.columns:
        fig_stack.add_trace(go.Bar(x=df['date'], y=df['new_user_cnt'], name='新用户'))
        fig_stack.add_trace(go.Bar(x=df['date'], y=df['old_user_cnt'], name='老用户'))
        fig_stack.update_layout(barmode='stack', title="新/老用户结构（堆叠）", xaxis_title="日期", yaxis_title="用户数", template="plotly_white")
    # 新用户占比折线（计算 new_user_cnt/(new+old)）
    if 'new_user_cnt' in df.columns and 'old_user_cnt' in df.columns:
        df['new_ratio'] = df['new_user_cnt'] / (df['new_user_cnt'] + df['old_user_cnt']).replace(0, np.nan)
        fig_ratio = px.line(df, x='date', y='new_ratio', title="新用户占比趋势", labels={'new_ratio':'新用户占比'})
        fig_ratio.update_yaxes(tickformat=".0%")
        # 最新日期饼图
        latest = df.iloc[-1]
        fig_pie = px.pie(names=['新用户','老用户'], values=[int(latest['new_user_cnt']), int(latest['old_user_cnt'])], title=f"最新日期 {latest['date'].date()} 新/老用户占比")
    else:
        fig_ratio = go.Figure()
        fig_pie = go.Figure()
    return fig_stack, fig_ratio, fig_pie

# ---------- DASH APP ----------
def create_app():
    df_active, df_date, df_newold = read_parquets()
    fig_line, cards, last_date = build_active_figures(df_active, df_date)
    fig_stack, fig_ratio, fig_pie = build_newold_figures(df_newold)

    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # render card images
    card_imgs = []
    for k, v in cards.items():
        title = k
        value = v['today']
        subtitle = f"7d avg {v['7d_avg']}  • 30d avg {v['30d_avg']}"
        img_b64 = render_card_image(title, value, subtitle)
        card_imgs.append(img_b64)

    app.layout = dbc.Container([
        # Header row: 居中标题 + 下方按钮
        dbc.Row([
            dbc.Col(html.H3("用户规模与活跃 看板", style={"textAlign":"center", "marginBottom":"6px"}), width=12)
        ]),
        dbc.Row([
            dbc.Col(
                dbc.ButtonGroup([
                    dbc.Button("概览", id="btn-overview", color="primary", outline=False),
                    dbc.Button("新/老用户", id="btn-newold", color="secondary", outline=True),
                    dbc.Button("导出", id="btn-export", color="info", outline=True),
                ], style={"display":"flex", "justifyContent":"center", "gap":"8px"}),
                width=12
            )
        ], className="mb-3"),
        # 顶部空白
        dbc.Row([], style={"height": "12px"}),
        # 三张卡片：稍微缩小并加阴影与内边距
        dbc.Row([
            dbc.Col(html.Div(html.Img(src=card_imgs[0], style={"width":"92%","height":"92%","display":"block","margin":"0 auto","boxShadow":"0 2px 6px rgba(0,0,0,0.12)"}), style={"padding":"6px"}), width=4, lg=3, md=4, sm=6),
            dbc.Col(html.Div(html.Img(src=card_imgs[1], style={"width":"92%","height":"92%","display":"block","margin":"0 auto","boxShadow":"0 2px 6px rgba(0,0,0,0.12)"}), style={"padding":"6px"}), width=4, lg=3, md=4, sm=6),
            dbc.Col(html.Div(html.Img(src=card_imgs[2], style={"width":"92%","height":"92%","display":"block","margin":"0 auto","boxShadow":"0 2px 6px rgba(0,0,0,0.12)"}), style={"padding":"6px"}), width=4, lg=3, md=4, sm=6),
        ], className="mb-3", style={"display":"flex", "justifyContent":"space-between", "alignItems":"center"}),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_line), width=12)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_stack), width=8),
            dbc.Col(dcc.Graph(figure=fig_pie), width=4),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_ratio), width=12)
        ])
    ],
    fluid=True,
    style={
        "paddingTop":"16px",
        "paddingBottom":"16px",
        "paddingLeft":"28px",
        "paddingRight":"28px",
        "marginTop":"12px",
        "marginBottom":"12px",
        "marginLeft":"12px",
        "marginRight":"12px",
        "backgroundColor":"#ffffff"
    })
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8050)