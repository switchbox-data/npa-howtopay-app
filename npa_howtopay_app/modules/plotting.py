import plotly.express as px
import plotly.graph_objects as go


# Define Switchbox color palette
switchbox_colors = {
    'Gas Opex': '#68BED8',      # sb-sky
    'Gas Capex': '#546800', # sb-pistachio-text
    'Electric Opex': '#A0AF12', # sb-pistachio 
    'Electric Capex': '#023047',     # sb-midnight  
    'Taxpayer': '#FC9706', # sb-carrot
}

def plot_ratebase(df, my_colors=switchbox_colors):
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

    # Remove the "=" prefix from facet labels and make them bold
    fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text.split('=')[-1]}</b>"))
    fig.for_each_yaxis(lambda y: y.update(title=''))
    
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