import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from typing import Dict, Tuple
import numpy as np


# Define Switchbox color palette
switchbox_colors = {
    'gas_opex': '#68BED8',      # sb-sky
    'gas_capex': '#546800', # sb-pistachio-text
    'electric_opex': '#A0AF12', # sb-pistachio 
    'electric_capex': '#023047',     # sb-midnight  
    'taxpayer': '#FC9706', # sb-carrot
}

line_styles = {
    'gas_opex': 'dash',
    'gas_capex': 'solid',
    'electric_opex': 'dash',
    'electric_capex': 'solid',
    'taxpayer': 'solid',
}

scenario_labels = {
    'gas_opex': 'Gas Opex',
    'gas_capex': 'Gas Capex',
    'electric_opex': 'Electric Opex',
    'electric_capex': 'Electric Capex',
    'taxpayer': 'Taxpayer',
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
        return ('$,.1f', 'B', 1_000_000_000)
    elif max_abs_value >= 1_000_000:  # Millions
        return ('$,.1f', 'M', 1_000_000)
    elif max_abs_value >= 1_000:  # Thousands
        return ('$,.0f', 'K', 1_000)
    else:  # Less than thousands
        return ('$,.0f', '', 1)
        
def plot_utility_metric(
    plt_df: pl.DataFrame, 
    column: str, 
    title: str, 
    y_label_unit: str = "$", 
    scenario_colors: Dict[str, str] = switchbox_colors,
    scenario_line_styles: Dict[str, str] = line_styles,
    show_absolute: bool = False
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
        tick_format, suffix, scale_factor = detect_magnitude_and_format(plt_df[column])
        # Scale the data for display
        plt_df = plt_df.with_columns(
            (pl.col(column) / scale_factor).alias(f"{column}_scaled")
        )
        plot_column = f"{column}_scaled"
        # Update y-axis label with suffix
        y_label_with_suffix = f"{y_label_unit}{suffix}" if suffix else y_label_unit
    else:
        # For non-dollar units, use original formatting
        tick_format = '.3f' if "/" in y_label_unit else ',.0f'
        suffix = ""
        plot_column = column
        y_label_with_suffix = y_label_unit

    # Determine y-axis label based on show_absolute parameter
    y_label = f"Absolute Value ({y_label_with_suffix})" if show_absolute else f"Delta from BAU ({y_label_with_suffix})"
    
    print("Creating plotly figure...")
    # Create figure with facets
    fig = px.line(
        plt_df,
        x="year",
        y=plot_column,
        color="scenario_id",
        line_dash="scenario_id",
        facet_col="utility_type",
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
    print("Figure created successfully")
    
    # Remove the "=" prefix from facet labels and make them bold, capitalize
    fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text.split('=')[-1].upper()}</b>"))
    
    # Remove y-axis titles from individual facets
    fig.for_each_yaxis(lambda y: y.update(title=''))
    
    # Add main y-axis label
    fig.add_annotation(
        x=-0.1,
        y=0.5,
        text=y_label,
        textangle=-90,
        showarrow=False,
        xref="paper",
        yref="paper"
    )
    
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
    
    # Format y-axis based on unit type
    if y_label_unit == "$":
        fig.update_yaxes(tickformat=tick_format)
    elif "/" in y_label_unit:  # For rates like $/kWh
        fig.update_yaxes(tickformat='.2f')
    
    return fig

def plot_grid(df, my_colors=switchbox_colors):
    """Plot grid of ratebase and delivery charges over time"""
    

    
    fig = px.line(
        df, 
        x='year', 
        y='delivery_charges',
        color='scenario',
        color_discrete_map=my_colors,
        facet_col='utility',
        facet_row='npa_status',
        title='',
        labels={
            'delivery_charges': '', 
            'year': 'Year',
            'utility': '',
            'npa_status': '',
            'scenario': 'Scenario'
        }
    )

    # Position legend on bottom
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.2,
            xanchor="center",
            x=0.5
        )
    )

    # Remove the "=" prefix from facet labels and make them bold
    fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text.split('=')[-1]}</b>"))
    fig.for_each_yaxis(lambda y: y.update(title=''))
    # Format y-axis to show currency - use update_yaxes() not update_yaxis()
    fig.update_yaxes(tickformat='$,.0f')

    fig.add_annotation(
    x=-0.1,  # Adjust x-coordinate for positioning
    y=0.5,   # Adjust y-coordinate for vertical centering
    text="Average Delivery Charges ($)",
    textangle=-90,  # Rotate text for vertical orientation
    showarrow=False,
    xref="paper",
    yref="paper"
    )
    return fig