import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from typing import Dict, Tuple
import numpy as np


# Define Switchbox color palette
switchbox_colors = {
    'gas_opex': '#A0AF12',  # sb-pistachio 
    'gas_capex': '#546800',  # sb-pistachio-text
    'electric_opex': '#68BED8',      # sb-sky
    'electric_capex': '#023047',     # sb-midnight
    'taxpayer': '#FC9706',  # sb-carrot
    'bau': '#FFC729', # sb-saffron
    'performance_incentive': '#000000',
}

line_styles = {
    'gas_opex': 'dash',
    'gas_capex': 'solid',
    'electric_opex': 'dash',
    'electric_capex': 'solid',
    'taxpayer': 'solid',
    'bau': 'solid',
    'performance_incentive': 'solid',
}

scenario_labels = {
    'gas_opex': 'Gas Opex',
    'gas_capex': 'Gas Capex',
    'electric_opex': 'Electric Opex',
    'electric_capex': 'Electric Capex',
    'taxpayer': 'Taxpayer',
    'bau': 'BAU',
    'performance_incentive': 'Performance Incentive',
}

def detect_magnitude_and_format(data_values: pl.Series) -> Tuple[str, str, float]:
    """
    Detect the magnitude of data values and return appropriate format and scale.
    
    Args:
        data_values: Polars Series containing the data values to analyze
        
    Returns:
        Tuple of (tick_format, suffix, scale_factor)
    """
    # Get the maximum absolute value to determine scale
    max_abs_value = float(data_values.abs().max())
    
    if max_abs_value >= 1_000_000_000:  # Billions
        return ('$,.1f', ' Billion', 1_000_000_000, ' B')
    elif max_abs_value >= 1_000_000:  # Millions
        return ('$,.1f', ' Million', 1_000_000, ' M')
    elif max_abs_value >= 100_000:  # Thousands
        return ('$,.0f', ' Thousand', 1_000, ' K')
    elif max_abs_value >= 10:  # Between $10 and $999
        return ('$,.0f', '', 1, '')
    elif max_abs_value >= 1:  # Between $1 and $9.99
        return ('$.2f', '', 1, '')  # Changed from '$,.2f' to '$.2f'
    else:
        return ('$,.3f', '', 1, '')

def apply_plot_theme(fig):
    """
    Apply consistent theme with white background and gray grid lines
    
    Args:
        fig: Plotly figure object
    
    Returns:
        Modified figure with applied theme
    """
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black')
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='lightgray'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='lightgray',
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='darkgray'
    )
    
    return fig

def plot_utility_metric(
    plt_df: pl.DataFrame, 
    column: str, 
    title: str, 
    y_label_unit: str = "$", 
    y_label_title: str = "",
    scenario_colors: Dict[str, str] = switchbox_colors,
    scenario_line_styles: Dict[str, str] = line_styles,
    show_absolute: bool = False,
    show_year: int = None
) :
    """
    Generic utility plotting function for faceted plots (Gas/Electric)
    
    Args:
        plt_df: DataFrame with utility data in long format
        column: Column name to plot
        title: Title for the plot
        y_label_unit: Unit for y-axis label (e.g., "$", "$/unit", "$/kWh")
        scenario_colors: Dictionary mapping scenario_id to colors
        show_absolute: Whether to show absolute values or deltas (default: False for delta)
    """

    # Detect magnitude and get appropriate formatting for y-axis
    if y_label_unit == "$":
        tick_format, suffix, scale_factor, short_suffix = detect_magnitude_and_format(plt_df[column])
        # Scale the data for display
        plt_df = plt_df.with_columns(
            (pl.col(column) / scale_factor).alias(f"{column}_scaled")
        )
        plot_column = f"{column}_scaled"
        # Update y-axis label with suffix
        y_label_with_suffix = f"{y_label_unit}{suffix}" if suffix else y_label_unit
    elif "%" in y_label_unit:
        # Scale the data for display
        plt_df = plt_df.with_columns(
            (pl.col(column) * 100).alias(f"{column}_scaled")
        )
        tick_format = '.2f'
        suffix = "%"
        plot_column = f"{column}_scaled"
        y_label_with_suffix = '%'
    else:
        # For non-dollar units, use original formatting
        tick_format = '.3f' if "/" in y_label_unit else ',.0f'
        suffix = ""
        plot_column = column
        y_label_with_suffix = y_label_unit

    # Determine y-axis label based on show_absolute parameter
    if show_absolute:
        y_label = f"{y_label_title} ({y_label_with_suffix})"
    else:
        # Use delta symbol (Δ) for delta values
        y_label = f"Δ {y_label_title} ({y_label_with_suffix})"
    
    print("Creating plotly figure...")
    # Create figure with facets
    fig = px.line(
        plt_df,
        x="year",
        y=plot_column,
        color="scenario_id",
        line_dash="scenario_id",
        facet_col="utility_type",
        facet_col_spacing=0.09,
        color_discrete_map=scenario_colors,
        line_dash_map=scenario_line_styles,
        title="",
        labels={
            plot_column: y_label,
            "year": "Year",
            "utility_type": "",
            "scenario_id": "Scenario"
        }
    )
    print(f"Figure created successfull - {y_label}")
    # INSERT_YOUR_CODE
    # Add a gray vertical line at show_year if plotting converts or nonconverts bill per user
    # if column in ("converts_bill_per_user", "nonconverts_bill_per_user") and show_year is not None:
    #     try:
    #         show_year_val = int(show_year)
    #         fig.add_vline(
    #             x=show_year_val,
    #             line_dash="dash",
    #             line_color="gray",
    #             line_width=2,
    #             annotation_text="",
    #             annotation_position="top"
    #         )
    #     except Exception:
    #         pass
    # Remove the "=" prefix from facet labels and make them bold, capitalize
    fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text.split('=')[-1].upper()}</b>"))
    
    # Remove y-axis titles from individual facets
    # fig.for_each_yaxis(lambda y: y.update(title=''))
    # Remove y-axis title from second facet
    fig.update_yaxes(title=None, col=2)
    # Align y-axis title to the right

    # # Add main y-axis label
    # fig.add_annotation(
    #     x=-0.15,
    #     y=0.5,
    #     text=y_label,
    #     textangle=-90,
    #     showarrow=False,
    #     xref="paper",
    #     yref="paper"
    # )
    
    # Update legend labels
    fig.for_each_trace(lambda t: t.update(name=scenario_labels[t.name]))
    
    # Update layout without title
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.4,
            xanchor="center",
            x=0.5
        )
    )
    
    # Add horizontal line at y=0
    if not show_absolute:
        fig.add_hline(y=0, line_dash="solid", line_color="darkgray", line_width=1)
    
    # Format y-axis based on unit type
    if y_label_unit == "$":
        fig.update_yaxes(tickformat=tick_format,
        ticksuffix=short_suffix,  # Add " units" as the suffix
        # title=y_label # Optional: Set a y-axis title
        )
    elif "%" in y_label_unit:
        fig.update_yaxes(
        ticksuffix=" %",  # Add " units" as the suffix
        )
    elif "/" in y_label_unit:  # For rates like $/kWh
        fig.update_yaxes(tickformat='.3f')
    
    # Apply theme
    fig = apply_plot_theme(fig)
    
    return fig

def plot_total_bills_bar(
    results_df: pl.DataFrame, 
    converts_nonconverts: str ,
    show_absolute: bool,
    y_label_title: str = "",
    scenario_colors: Dict[str, str] = switchbox_colors,
    scenario_line_styles: Dict[str, str] = line_styles,
     
) -> go.Figure:
    """
    Plot total bills faceted by converts/nonconverts using Plotly
    
    Args:
        results_df: DataFrame with bill data
        scenario_colors: Dictionary mapping scenario_id to colors
        scenario_line_styles: Dictionary mapping scenario_id to line styles
        show_absolute: Whether to show absolute values or deltas (default: False for delta)
    """
    
    # Reshape data for plotly - create long format with user_type facet
    converts_data = results_df.select([
        "year", "scenario_id", "converts_total_bill_per_user"
    ]).with_columns(
        pl.lit("CONVERTS").alias("user_type"),
        pl.col("converts_total_bill_per_user").alias("total_bill")
    ).drop("converts_total_bill_per_user")
    
    nonconverts_data = results_df.select([
        "year", "scenario_id", "nonconverts_total_bill_per_user"
    ]).with_columns(
        pl.lit("NONCONVERTS").alias("user_type"),
        pl.col("nonconverts_total_bill_per_user").alias("total_bill")
    ).drop("nonconverts_total_bill_per_user")
    
    # Combine data
    plt_df = converts_data if converts_nonconverts == "converts" else nonconverts_data
    
    # Detect magnitude and get appropriate formatting for y-axis
    tick_format, suffix, scale_factor, short_suffix = detect_magnitude_and_format(plt_df["total_bill"])
    
    # Scale the data for display
    plt_df = plt_df.with_columns(
        (pl.col("total_bill") / scale_factor).alias("total_bill_scaled")
    )
    
    # # Update y-axis label with suffix
    # # y_label_with_suffix = f"${suffix}" if suffix else "$"
    # if converts_nonconverts == "nonconverts":
    #     y_label = f"Combined Annual Delivery Bills (absolute value)" if show_absolute else f"Combined Annual Delivery Bills\n(Delta from BAU)"
    # elif converts_nonconverts == "converts":
    #     y_label = f"Combined Annual Delivery Bills (absolute value)" if show_absolute else f"Change in combined annual delivery bills (after electrification)"
        # Determine y-axis label based on show_absolute parameter
    if show_absolute:
        y_label = f"{y_label_title} ($)"
    else:
        # Use delta symbol (Δ) for delta values
        y_label = f"Δ {y_label_title} ($)"

    print("Creating plotly figure...")
    # Create figure with facets
    fig = px.bar(
        plt_df,
        x="scenario_id",
        y="total_bill",
        color="scenario_id",
        # facet_col="user_type",
        color_discrete_map=scenario_colors,
        title="",
        labels={
            "total_bill": y_label,
            "year": "Year",
            "user_type": "",
            "scenario_id": ""
        }
    )
    print("Figure created successfully")
    
    # Remove the "=" prefix from facet labels and make them bold, capitalize
    # fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text.split('=')[-1]}</b>"))
    
    # # Remove y-axis titles from individual facets
    # fig.for_each_yaxis(lambda y: y.update(title=''))
    
    # # Add main y-axis label
    # fig.add_annotation(
    #     x=-0.1,
    #     y=0.5,
    #     text="User Bills (Total)",
    #     textangle=-90,
    #     showarrow=False,
    #     xref="paper",
    #     yref="paper"
    # )
    
    # Update x-axis labels to use scenario_labels
    unique_scenarios = sorted(plt_df["scenario_id"].unique().to_list())
    fig.update_xaxes(ticktext=[scenario_labels.get(x, x) for x in unique_scenarios],
                    tickvals=unique_scenarios)
    
    # Hide legend
    fig.update_layout(
        showlegend=False,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.4,
            xanchor="center",
            x=0.5
        )
    )
    
    # Format y-axis with detected tick format
    fig.update_yaxes(tickformat=tick_format)
    
    # Apply theme
    fig = apply_plot_theme(fig)
    
    return fig


def plot_total_bills_ts(
    delta_bau_df: pl.DataFrame, 
    converts_nonconverts: str,
    show_absolute: bool,
    y_label_title: str = "",
    show_year: int = None,
    scenario_colors: Dict[str, str] = switchbox_colors,
    scenario_line_styles: Dict[str, str] = line_styles,
    
) -> go.Figure:
    """
    Plot total bills faceted by converts/nonconverts using Plotly
    
    Args:
        delta_bau_df: DataFrame with bill data
        scenario_colors: Dictionary mapping scenario_id to colors
        scenario_line_styles: Dictionary mapping scenario_id to line styles
        show_absolute: Whether to show absolute values or deltas (default: False for delta)
    """
    
    # Reshape data for plotly - create long format with user_type facet
    converts_data = delta_bau_df.select([
        "year", "scenario_id", "converts_total_bill_per_user"
    ]).with_columns(
        pl.lit("CONVERTS").alias("user_type"),
        pl.col("converts_total_bill_per_user").alias("total_bill")
    ).drop("converts_total_bill_per_user")
    
    nonconverts_data = delta_bau_df.select([
        "year", "scenario_id", "nonconverts_total_bill_per_user"
    ]).with_columns(
        pl.lit("NONCONVERTS").alias("user_type"),
        pl.col("nonconverts_total_bill_per_user").alias("total_bill")
    ).drop("nonconverts_total_bill_per_user")
    
    # Combine data
    plt_df = converts_data if converts_nonconverts == "converts" else nonconverts_data
    
    # Detect magnitude and get appropriate formatting for y-axis
    tick_format, suffix, scale_factor, short_suffix = detect_magnitude_and_format(plt_df["total_bill"])
    
    # Scale the data for display
    plt_df = plt_df.with_columns(
        (pl.col("total_bill") / scale_factor).alias("total_bill_scaled")
    )
    
    if show_absolute:
        y_label = f"{y_label_title} ($)"
    else:
        # Use delta symbol (Δ) for delta values
        y_label = f"Δ {y_label_title} ($)"
    
    print("Creating plotly figure...")
    # Create figure with facets
    fig = px.line(
        plt_df,
        x="year",
        y="total_bill",
        color="scenario_id",
        line_dash="scenario_id",
        # facet_col="user_type",
        color_discrete_map=scenario_colors,
        line_dash_map=scenario_line_styles,
        title="",
        labels={
            "total_bill": y_label,
            "year": "Year",
            "user_type": "",
            "scenario_id": "Scenario"
        }
    )
    print("Figure created successfully")
    
    # # Remove the "=" prefix from facet labels and make them bold, capitalize
    # fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text.split('=')[-1]}</b>"))
    
    # # Remove y-axis titles from individual facets
    # fig.for_each_yaxis(lambda y: y.update(title=''))
    
    # # Add main y-axis label
    # fig.add_annotation(
    #     x=-0.1,
    #     y=0.5,
    #     text="User Bills (Total)",
    #     textangle=-90,
    #     showarrow=False,
    #     xref="paper",
    #     yref="paper"
    # )
    show_year_val = int(show_year)
    fig.add_vline(
        x=show_year_val,
        line_dash="dash",
        line_color="gray",
        line_width=2,
        annotation_text="",
        annotation_position="top"
    )
    # Update legend labels to use scenario_labels
    fig.for_each_trace(lambda t: t.update(name=scenario_labels.get(t.name, t.name)))
    
    # Update layout to match plot_utility_metric style
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.4,
            xanchor="center",
            x=0.5
        )
    )
    
    # Add horizontal line at y=0
    if not show_absolute:
        fig.add_hline(y=0, line_dash="solid", line_color="darkgray", line_width=1)
    
    # Format y-axis with detected tick format
    fig.update_yaxes(tickformat=tick_format)
    
    # Apply theme
    fig = apply_plot_theme(fig)
    
    return fig