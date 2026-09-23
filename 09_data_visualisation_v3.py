# 09_data_visualisation_v3.py
from dash import Dash, html, dcc, Input, Output
import dash
import dash_bootstrap_components as dbc
import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location(
    "active_users_dashboard_09",
    str(pathlib.Path(__file__).with_name("09_active_users_dashboard.py"))
)
_viz_active_users_dashboard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_viz_active_users_dashboard)


_spec = importlib.util.spec_from_file_location(
    "task_completion_lifecycle_analysis_data_vis_09",
    str(pathlib.Path(__file__).with_name("09_task_completion_lifecycle_analysis_data_vis.py"))
)
_viz_task_completion_lifecycle_analysis_data_vis = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_viz_task_completion_lifecycle_analysis_data_vis)

_spec = importlib.util.spec_from_file_location(
    "in_depth_analysis_of_feature_usage_09",
    str(pathlib.Path(__file__).with_name("09_in-depth_analysis_of_feature_usage.py"))
)
_viz_in_depth_analysis_of_feature_usage = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_viz_in_depth_analysis_of_feature_usage)



# 顶部两行 header（保留）
header_rows = [
    dbc.Row(
        [
            dbc.Col(
                html.H3("用户规模与活跃 看板", style={"textAlign": "center", "marginBottom": "6px"}),
                width=12
            )
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                dbc.ButtonGroup(
                    [
                        dbc.Button("用户规模与活跃看板", id="btn-overview", color="primary", outline=False),
                        dbc.Button("任务完成与生命周期分析", id="btn-newold", color="secondary", outline=True),
                        dbc.Button("功能使用深度分析", id="btn-export", color="info", outline=True),
                    ],
                    style={"display": "flex", "justifyContent": "center", "gap": "8px"},
                ),
                width=12,
            )
        ],
        className="mb-3",
    ),
]

def main():
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )

    # 主布局：header + 内容占位
    app.layout = dbc.Container(
        [
            *header_rows,
            html.Div(id="main-content")
        ],
        fluid=True,
        style={"paddingTop": "16px", "paddingBottom": "16px", "paddingLeft": "28px", "paddingRight": "28px"}
    )

    # 首次加载时显示 overview
    @app.callback(
        Output("main-content", "children"),
        [Input("btn-overview", "n_clicks"), Input("btn-newold", "n_clicks"), Input("btn-export", "n_clicks")],
        prevent_initial_call=False
    )
    def switch_section(n_overview, n_newold, n_export):
        ctx = dash.callback_context
        if not ctx.triggered:
            # 初始显示 overview（模块内部会读取并缓存数据）
            return _viz_active_users_dashboard.render_overview()
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if btn_id == "btn-newold":
            return _viz_task_completion_lifecycle_analysis_data_vis.render_newold()
        if btn_id == "btn-export":
            return _viz_in_depth_analysis_of_feature_usage.render_export()
        return _viz_active_users_dashboard.render_overview()

    @app.callback(
        Output("newold-pie", "figure"),
        Input("newold-date", "value")
    )
    def update_newold_pie(selected_date):
        return _viz_active_users_dashboard.newold_pie_figure(selected_date)
    
    return app

if __name__ == "__main__":
    app = main()
    app.run(debug=True, port=8050)