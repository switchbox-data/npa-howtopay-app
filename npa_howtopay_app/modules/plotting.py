import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from typing import Dict


# Define Switchbox color palette
switchbox_colors = {
    'Gas Opex': '#68BED8',      # sb-sky
    'Gas Capex': '#546800', # sb-pistachio-text
    'Electric Opex': '#A0AF12', # sb-pistachio 
    'Electric Capex': '#023047',     # sb-midnight  
    'Taxpayer': '#FC9706', # sb-carrot
}

def plot_utility_metric(
    plt_df: pl.DataFrame, 
    column: str, 
    title: str, 
    y_label_unit: str = "$", 
    scenario_colors: Dict[str, str] = switchbox_colors, 
    show_absolute: bool = False
) -> go.Figure:
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

    # Determine y-axis label based on show_absolute parameter
    y_label = f"Absolute Value ({y_label_unit})" if show_absolute else f"Delta ({y_label_unit})"
    
    # Create figure with facets
    fig = px.line(
        plt_df,
        x="year",
        y=column,
        color="scenario_id",
        # line_dash="scenario_id",
        facet_col="utility_type",
        color_discrete_map=scenario_colors,
        title="",
        labels={
            column: y_label,
            "year": "Year",
            "utility_type": "",
            "scenario_id": "Scenario"
        }
    )
    
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
    
    # Update main title
    title_suffix = " (Absolute Values)" if show_absolute else " (Delta from BAU)"
    fig.update_layout(
        title={
            'text': f"<b>{title}{title_suffix}</b>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.15,
            xanchor="center",
            x=0.5
        )
    )
    
    # Format y-axis based on unit type
    if y_label_unit == "$":
        fig.update_yaxes(tickformat='$,.0f')
    elif "/" in y_label_unit:  # For rates like $/kWh
        fig.update_yaxes(tickformat='.3f')
    
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