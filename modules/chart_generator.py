"""Plotly chart generation helpers."""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


AGG_FUNCS = {
    "sum": "sum",
    "average": "mean",
    "mean": "mean",
    "count": "count",
    "min": "min",
    "max": "max",
}


def empty_figure(message: str = "No chart available. Map the required columns first."):
    fig = go.Figure()
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    fig.update_layout(height=360)
    return fig


def aggregate(df: pd.DataFrame, x: str, y: Optional[str] = None, color: Optional[str] = None, agg: str = "sum") -> pd.DataFrame:
    if not x or x not in df.columns:
        return pd.DataFrame()
    agg = AGG_FUNCS.get(agg, "sum")

    group_cols = [x]
    if color and color in df.columns:
        group_cols.append(color)

    if y and y in df.columns:
        tmp = df[group_cols + [y]].copy()
        if agg != "count":
            tmp[y] = pd.to_numeric(tmp[y], errors="coerce")
            tmp = tmp.dropna(subset=[y])
            if tmp.empty:
                return pd.DataFrame()
        out = tmp.groupby(group_cols, dropna=False)[y].agg(agg).reset_index()
    else:
        out = df.groupby(group_cols, dropna=False).size().reset_index(name="Count")
    return out


def make_chart(df: pd.DataFrame, chart_type: str, x: Optional[str], y: Optional[str] = None, color: Optional[str] = None, agg: str = "sum", title: Optional[str] = None):
    if df is None or df.empty:
        return empty_figure("No data available.")
    if not x or x not in df.columns:
        return empty_figure("Select a valid X-axis column.")

    chart_type = chart_type.lower()
    title = title or f"{chart_type.title()} Chart"

    if chart_type in {"line", "bar", "area", "pie", "treemap"}:
        agg_df = aggregate(df, x, y, color if chart_type not in {"pie", "treemap"} else None, agg)
        if agg_df.empty:
            return empty_figure()
        val_col = y if y and y in agg_df.columns else "Count"

        if chart_type == "line":
            return px.line(agg_df, x=x, y=val_col, color=color if color in agg_df.columns else None, markers=True, title=title)
        if chart_type == "bar":
            return px.bar(agg_df, x=x, y=val_col, color=color if color in agg_df.columns else None, title=title)
        if chart_type == "area":
            return px.area(agg_df, x=x, y=val_col, color=color if color in agg_df.columns else None, title=title)
        if chart_type == "pie":
            return px.pie(agg_df, names=x, values=val_col, title=title)
        if chart_type == "treemap":
            return px.treemap(agg_df, path=[x], values=val_col, title=title)

    if chart_type == "scatter":
        if not y or y not in df.columns:
            return empty_figure("Scatter plot needs X and Y columns.")
        tmp = df.copy()
        tmp[y] = pd.to_numeric(tmp[y], errors="coerce")
        tmp = tmp.dropna(subset=[y])
        if tmp.empty:
            return empty_figure("Scatter plot needs a numeric Y column.")
        return px.scatter(tmp, x=x, y=y, color=color if color in tmp.columns else None, trendline=None, title=title)

    if chart_type == "histogram":
        return px.histogram(df, x=x, color=color if color in df.columns else None, title=title)

    if chart_type == "box":
        if not y or y not in df.columns:
            tmp = df.copy()
            tmp[x] = pd.to_numeric(tmp[x], errors="coerce")
            tmp = tmp.dropna(subset=[x])
            if tmp.empty:
                return empty_figure("Box plot needs a numeric column.")
            return px.box(tmp, y=x, title=title)
        tmp = df.copy()
        tmp[y] = pd.to_numeric(tmp[y], errors="coerce")
        tmp = tmp.dropna(subset=[y])
        if tmp.empty:
            return empty_figure("Box plot needs a numeric Y column.")
        return px.box(tmp, x=x, y=y, color=color if color in tmp.columns else None, title=title)

    if chart_type == "heatmap":
        if not y or y not in df.columns:
            return empty_figure("Heatmap needs a numeric Y column.")
        if color and color in df.columns:
            agg_func = AGG_FUNCS.get(agg, "sum")
            tmp = df[[x, color, y]].copy()
            tmp[y] = pd.to_numeric(tmp[y], errors="coerce")
            tmp = tmp.dropna(subset=[y])
            if tmp.empty:
                return empty_figure("Heatmap needs a numeric Y column.")
            pivot = tmp.pivot_table(index=color, columns=x, values=y, aggfunc=agg_func, fill_value=0)
        else:
            if df.select_dtypes(include="number").shape[1] < 2:
                return empty_figure("Select Category/Color for grouped heatmap, or use at least two numeric columns.")
            pivot = df.select_dtypes(include="number").corr(numeric_only=True)
        return px.imshow(pivot, text_auto=True, aspect="auto", title=title)

    if chart_type == "pareto":
        if not y or y not in df.columns:
            return empty_figure("Pareto chart needs a numeric Y column.")
        return pareto_chart(df, x, y, title)

    return empty_figure("Unsupported chart type.")


def pareto_chart(df: pd.DataFrame, category_col: str, value_col: str, title: str = "Pareto Chart"):
    if category_col not in df.columns or value_col not in df.columns:
        return empty_figure()
    tmp = df[[category_col, value_col]].copy()
    tmp[value_col] = pd.to_numeric(tmp[value_col], errors="coerce")
    tmp = tmp.dropna(subset=[value_col])
    if tmp.empty:
        return empty_figure("Pareto chart needs a numeric Y column.")
    tmp = tmp.groupby(category_col, dropna=False)[value_col].sum().sort_values(ascending=False).reset_index()
    if tmp.empty:
        return empty_figure()
    total = tmp[value_col].sum()
    if total == 0:
        return empty_figure("Pareto chart needs a non-zero Y column.")
    tmp["Cumulative %"] = tmp[value_col].cumsum() / total * 100

    fig = go.Figure()
    fig.add_bar(x=tmp[category_col], y=tmp[value_col], name=value_col)
    fig.add_scatter(x=tmp[category_col], y=tmp["Cumulative %"], name="Cumulative %", yaxis="y2", mode="lines+markers")
    fig.update_layout(
        title=title,
        yaxis=dict(title=value_col),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 110]),
        legend=dict(orientation="h"),
        height=450,
    )
    return fig


def time_series(df: pd.DataFrame, date_col: str, value_col: str, freq: str = "M", title: str = "Trend"):
    if date_col not in df.columns or value_col not in df.columns:
        return empty_figure()
    tmp = df.copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp[value_col] = pd.to_numeric(tmp[value_col], errors="coerce")
    tmp = tmp.dropna(subset=[date_col, value_col])
    if tmp.empty:
        return empty_figure("Trend needs valid date and numeric value columns.")
    tmp["Period"] = tmp[date_col].dt.to_period(freq).dt.to_timestamp()
    agg = tmp.groupby("Period")[value_col].sum().reset_index()
    return px.line(agg, x="Period", y=value_col, markers=True, title=title)


def grouped_bar(df: pd.DataFrame, category_col: str, value_col: str, title: str):
    if category_col not in df.columns or value_col not in df.columns:
        return empty_figure()
    tmp = df[[category_col, value_col]].copy()
    tmp[value_col] = pd.to_numeric(tmp[value_col], errors="coerce")
    tmp = tmp.dropna(subset=[value_col])
    if tmp.empty:
        return empty_figure("Bar chart needs a numeric value column.")
    tmp = tmp.groupby(category_col, dropna=False)[value_col].sum().sort_values(ascending=False).reset_index()
    return px.bar(tmp, x=category_col, y=value_col, title=title)


def suggest_charts(df: pd.DataFrame, mapping: dict) -> list[str]:
    suggestions = []
    fields = {k: v for k, v in mapping.items() if v}
    if fields.get("Date") and fields.get("Demand"):
        suggestions.append("Monthly demand trend: Date vs Demand")
    if fields.get("Product") and fields.get("Sales"):
        suggestions.append("Product-wise sales bar chart")
    if fields.get("Supplier") and fields.get("Procurement Cost"):
        suggestions.append("Supplier-wise procurement cost")
    if fields.get("Route") and fields.get("Shipment Cost"):
        suggestions.append("Transportation cost per route")
    if fields.get("Warehouse") and fields.get("Inventory"):
        suggestions.append("Warehouse stock comparison")
    if fields.get("Category") and fields.get("Cost"):
        suggestions.append("Cost breakdown by category")
    if not suggestions:
        suggestions.append("Choose any categorical column as X and any numeric column as Y.")
    return suggestions


def chart_png_bytes(
    df: pd.DataFrame,
    chart_type: str,
    x: Optional[str],
    y: Optional[str] = None,
    color: Optional[str] = None,
    agg: str = "sum",
    title: str = "Smart Chart",
) -> bytes:
    """Render a static offline PNG with Matplotlib as a fallback export path."""
    mpl_config_dir = Path(__file__).resolve().parents[1] / "data" / ".matplotlib"
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))
    os.environ.setdefault("XDG_CACHE_HOME", str(mpl_config_dir))
    import matplotlib.pyplot as plt

    if df is None or df.empty or not x or x not in df.columns:
        raise ValueError("A valid X-axis column is required for PNG export.")

    chart_type = chart_type.lower()
    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    value_col = y if y and y in df.columns else None

    if chart_type in {"line", "bar", "area", "pie", "treemap"}:
        data = aggregate(df, x, value_col, color if chart_type in {"line", "bar", "area"} else None, agg)
        if data.empty:
            raise ValueError("No chart data available for PNG export.")
        measure = value_col if value_col and value_col in data.columns else "Count"

        if color and color in data.columns and chart_type in {"line", "bar", "area"}:
            pivot = data.pivot(index=x, columns=color, values=measure).fillna(0)
            if chart_type == "line":
                pivot.plot(ax=ax, marker="o")
            elif chart_type == "area":
                pivot.plot.area(ax=ax)
            else:
                pivot.plot.bar(ax=ax)
        elif chart_type == "pie":
            ax.pie(data[measure], labels=data[x].astype(str), autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
        else:
            plot_data = data.sort_values(measure, ascending=False).head(30)
            if chart_type == "line":
                ax.plot(plot_data[x].astype(str), plot_data[measure], marker="o")
            elif chart_type == "area":
                ax.fill_between(plot_data[x].astype(str), plot_data[measure], alpha=0.35)
                ax.plot(plot_data[x].astype(str), plot_data[measure], marker="o")
            else:
                ax.bar(plot_data[x].astype(str), plot_data[measure])
            ax.set_ylabel(str(measure))

    elif chart_type == "scatter":
        if not value_col:
            raise ValueError("Scatter PNG export needs a numeric Y column.")
        tmp = df[[x, value_col]].copy()
        tmp[value_col] = pd.to_numeric(tmp[value_col], errors="coerce")
        tmp = tmp.dropna(subset=[value_col])
        if tmp.empty:
            raise ValueError("Scatter PNG export needs a numeric Y column.")
        ax.scatter(tmp[x], tmp[value_col], alpha=0.75)
        ax.set_xlabel(str(x))
        ax.set_ylabel(str(value_col))

    elif chart_type == "histogram":
        series = pd.to_numeric(df[x], errors="coerce").dropna()
        if series.empty:
            counts = df[x].astype(str).value_counts().head(30)
            ax.bar(counts.index.astype(str), counts.values)
        else:
            ax.hist(series, bins=25)
        ax.set_xlabel(str(x))

    elif chart_type == "box":
        if value_col:
            grouped = df.groupby(x, dropna=False)
            groups = [pd.to_numeric(group[value_col], errors="coerce").dropna() for _, group in grouped]
            labels = [str(label) for label, _ in df.groupby(x, dropna=False)]
            groups_and_labels = [(group, label) for group, label in zip(groups, labels) if len(group)]
            if not groups_and_labels:
                raise ValueError("Box PNG export needs a numeric Y column.")
            groups, labels = zip(*groups_and_labels)
            ax.boxplot(groups, labels=labels, showfliers=False)
            ax.set_ylabel(str(value_col))
        else:
            ax.boxplot(pd.to_numeric(df[x], errors="coerce").dropna(), showfliers=False)

    elif chart_type == "heatmap":
        if not value_col:
            raise ValueError("Heatmap PNG export needs a numeric Y column.")
        if color and color in df.columns:
            pivot = df.pivot_table(index=color, columns=x, values=value_col, aggfunc=AGG_FUNCS.get(agg, "sum"), fill_value=0)
        else:
            pivot = df.select_dtypes(include="number").corr(numeric_only=True)
        image = ax.imshow(pivot, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)), labels=[str(c) for c in pivot.columns], rotation=45, ha="right")
        ax.set_yticks(range(len(pivot.index)), labels=[str(i) for i in pivot.index])
        fig.colorbar(image, ax=ax)

    elif chart_type == "pareto":
        if not value_col:
            raise ValueError("Pareto PNG export needs a numeric Y column.")
        data = df.groupby(x, dropna=False)[value_col].sum().sort_values(ascending=False).head(30)
        data = pd.to_numeric(data, errors="coerce").dropna()
        if data.empty or data.sum() == 0:
            raise ValueError("Pareto PNG export needs a non-zero numeric Y column.")
        cumulative = data.cumsum() / data.sum() * 100
        ax.bar(data.index.astype(str), data.values)
        ax2 = ax.twinx()
        ax2.plot(data.index.astype(str), cumulative.values, color="#0f766e", marker="o")
        ax2.set_ylabel("Cumulative %")
        ax.set_ylabel(str(value_col))

    else:
        raise ValueError("Unsupported chart type for PNG export.")

    ax.set_title(title)
    if chart_type not in {"pie", "heatmap"}:
        ax.tick_params(axis="x", labelrotation=45)
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=160)
    plt.close(fig)
    return buffer.getvalue()
