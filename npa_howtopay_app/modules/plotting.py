import plotly.express as px
import plotly.graph_objects as go

def plot_ratebase(df):
    """Plot utility ratebase over time"""
    # Reshape to long format
    df_long = df.melt(
        id_vars=['Year'], 
        value_vars=['Electric', 'Gas'],
        variable_name='utility',
        value_name='Ratebase'
    )
    
    fig = px.line(
        df_long, 
        x='Year', 
        y='Ratebase', 
        facet_col='utility',
        title='',
        labels={
            'Ratebase': 'Ratebase ($)', 
            'Year': 'Year',
            'utility': ''
        }
    )

    # Remove the "=" prefix from facet labels
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    # Format y-axis to show currency - use update_yaxes() not update_yaxis()
    fig.update_yaxes(tickformat='$,.0f')
    
    return fig

def plot_grid(df):
    """Plot grid of ratebase and delivery charges over time"""
    fig = px.line(
        df, 
        x='year', 
        y='delivery_charges', 
        facet_col='utility',
        facet_row='npa_status',
        title='',
        labels={
            'delivery_charges': '', 
            'year': 'Year',
            'utility': '',
            'npa_status': ''
        }
    )

    # Remove the "=" prefix from facet labels
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
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