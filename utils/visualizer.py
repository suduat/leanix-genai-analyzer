import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

QUADRANT_COLORS = {
    "Invest":    "#1D9E75",
    "Modernize": "#EF9F27",
    "Retire":    "#E24B4A",
    "Monitor":   "#555553",
}

FONT = dict(family="Arial, sans-serif", color="#1a1a1a")

LAYOUT_BASE = dict(
    font=FONT,
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    title_font=dict(size=15, color="#1a1a1a", family="Arial, sans-serif"),
    legend=dict(
        font=dict(size=12, color="#1a1a1a"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e0e0e0",
        borderwidth=1,
    ),
)


def scatter_quadrant(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="tech_debt_score",
        y="business_value_score",
        color="rationalization_quadrant",
        color_discrete_map=QUADRANT_COLORS,
        hover_name="app_name",
        hover_data={
            "business_capability": True,
            "lifecycle_stage": True,
            "annual_cost_usd": ":$,.0f",
            "hosting_type": True,
            "tech_debt_score": True,
            "business_value_score": True,
            "rationalization_quadrant": False,
        },
        size="annual_cost_usd",
        size_max=28,
        labels={
            "tech_debt_score": "Tech debt score →",
            "business_value_score": "Business value score →",
            "rationalization_quadrant": "Recommended action",
        },
        title="📊 Portfolio rationalization quadrant — tech debt vs business value",
    )

    # Quadrant shading
    fig.add_shape(type="rect", x0=0, y0=5, x1=5, y1=10,
                  fillcolor="#EAF3DE", opacity=0.35, line_width=0)
    fig.add_shape(type="rect", x0=5, y0=5, x1=10, y1=10,
                  fillcolor="#FAEEDA", opacity=0.35, line_width=0)
    fig.add_shape(type="rect", x0=0, y0=0, x1=5, y1=5,
                  fillcolor="#E6F1FB", opacity=0.35, line_width=0)
    fig.add_shape(type="rect", x0=5, y0=0, x1=10, y1=5,
                  fillcolor="#FCEBEB", opacity=0.35, line_width=0)

    # Quadrant labels — dark, readable
    for text, x, y, color in [
        ("✅ Invest", 2.5, 9.4, "#1D6B4E"),
        ("⚠️ Modernize", 7.5, 9.4, "#7A5200"),
        ("👁 Monitor", 2.5, 0.6, "#1A4F7A"),
        ("❌ Retire", 7.5, 0.6, "#8B1A1A"),
    ]:
        fig.add_annotation(
            x=x, y=y, text=f"<b>{text}</b>",
            showarrow=False,
            font=dict(size=12, color=color, family="Arial, sans-serif"),
        )

    fig.add_hline(y=5, line_dash="dot", line_color="#aaaaaa", line_width=1)
    fig.add_vline(x=5, line_dash="dot", line_color="#aaaaaa", line_width=1)

    fig.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(
            range=[0, 10.5], dtick=1,
            title_font=dict(size=13, color="#1a1a1a"),
            tickfont=dict(size=12, color="#1a1a1a"),
            showgrid=True, gridcolor="#eeeeee",
        ),
        yaxis=dict(
            range=[0, 10.5], dtick=1,
            title_font=dict(size=13, color="#1a1a1a"),
            tickfont=dict(size=12, color="#1a1a1a"),
            showgrid=True, gridcolor="#eeeeee",
        ),
        legend_title_text="Recommended action",
        height=500,
        margin=dict(l=50, r=20, t=60, b=50),
    )
    return fig


def lifecycle_bar(df: pd.DataFrame):
    order = ["Plan", "Phase In", "Active", "Phase Out", "End of Life"]
    colors = {
        "Plan":        "#AFA9EC",
        "Phase In":    "#378ADD",
        "Active":      "#1D9E75",
        "Phase Out":   "#EF9F27",
        "End of Life": "#E24B4A",
    }
    counts = (
        df["lifecycle_stage"]
        .value_counts()
        .reindex([s for s in order if s in df["lifecycle_stage"].unique()])
        .reset_index()
    )
    counts.columns = ["lifecycle_stage", "count"]

    fig = px.bar(
        counts,
        x="count",
        y="lifecycle_stage",
        orientation="h",
        color="lifecycle_stage",
        color_discrete_map=colors,
        text="count",
        title="📋 Apps by lifecycle stage",
        labels={"count": "Number of apps", "lifecycle_stage": ""},
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=13, color="#1a1a1a"),
    )
    fig.update_layout(
        **LAYOUT_BASE,
        showlegend=False,
        height=300,
        margin=dict(l=10, r=50, t=55, b=40),
        xaxis=dict(
            showgrid=True, gridcolor="#eeeeee",
            tickfont=dict(size=12, color="#1a1a1a"),
            title_font=dict(size=12, color="#1a1a1a"),
        ),
        yaxis=dict(
            tickfont=dict(size=13, color="#1a1a1a"),
            showgrid=False,
        ),
    )
    return fig


def cost_by_hosting(df: pd.DataFrame):
    cost = (
        df.groupby("hosting_type")["annual_cost_usd"]
        .sum()
        .reset_index()
    )
    cost.columns = ["hosting_type", "annual_cost_usd"]

    colors = {
        "On-Premise": "#7F77DD",
        "SaaS":       "#1D9E75",
        "Cloud":      "#378ADD",
    }

    fig = px.pie(
        cost,
        names="hosting_type",
        values="annual_cost_usd",
        color="hosting_type",
        color_discrete_map=colors,
        hole=0.52,
        title="💰 Annual cost by hosting type",
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{percent:.0%}",
        textposition="outside",
        textfont=dict(size=12, color="#1a1a1a"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}/yr<br>%{percent:.1%}<extra></extra>",
        pull=[0.03, 0.03, 0.03],
    )
    fig.update_layout(
        **LAYOUT_BASE,
        height=300,
        margin=dict(l=20, r=20, t=55, b=20),
    )
    fig.update_layout(
        legend=dict(
            font=dict(size=12, color="#1a1a1a"),
            orientation="h",
            yanchor="bottom",
            y=-0.18,
        )
    )
    return fig


def capability_heatmap(df: pd.DataFrame):
    cap_stats = (
        df.groupby("business_capability")
        .agg(
            avg_debt=("tech_debt_score", "mean"),
            avg_value=("business_value_score", "mean"),
            app_count=("app_name", "count"),
            total_cost=("annual_cost_usd", "sum"),
        )
        .round(1)
        .reset_index()
        .sort_values("avg_debt", ascending=True)
    )

    bar_colors = [
        "#E24B4A" if v >= 7 else "#EF9F27" if v >= 5 else "#1D9E75"
        for v in cap_stats["avg_debt"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=cap_stats["business_capability"],
        x=cap_stats["avg_debt"],
        name="Avg tech debt score",
        orientation="h",
        marker_color=bar_colors,
        customdata=cap_stats[["avg_value", "app_count", "total_cost"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg tech debt: %{x:.1f} / 10<br>"
            "Avg business value: %{customdata[0]:.1f} / 10<br>"
            "App count: %{customdata[1]}<br>"
            "Total cost: $%{customdata[2]:,.0f}<extra></extra>"
        ),
        text=cap_stats["avg_debt"].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        textfont=dict(size=13, color="#1a1a1a"),
    ))

    fig.add_vline(
        x=7, line_dash="dot", line_color="#E24B4A", line_width=1.5,
        annotation_text="<b>High debt threshold (7)</b>",
        annotation_position="top right",
        annotation_font=dict(color="#C0392B", size=11),
    )

    fig.update_layout(
        **LAYOUT_BASE,
        title="🏢 Avg tech debt score by business capability",
        xaxis=dict(
            range=[0, 11.5],
            title="Avg tech debt score (0–10)",
            title_font=dict(size=13, color="#1a1a1a"),
            tickfont=dict(size=12, color="#1a1a1a"),
            showgrid=True, gridcolor="#eeeeee", dtick=1,
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=13, color="#1a1a1a"),
            showgrid=False,
        ),
        height=400,
        margin=dict(l=10, r=80, t=60, b=40),
        showlegend=False,
    )
    return fig