# Import required libraries
from calendar import c
from multiprocessing.sharedctypes import Value
from click import style
from matplotlib.pyplot import step
from numpy import mask_indices
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# create function to get the site names 

def get_sites_options():
    df = spacex_df['Launch Site'].value_counts().to_frame().reset_index()
    options = [{'label': 'All Sites', 'value':'all'}]
    for index,site in df['index'].iteritems():
        options.append({'label': site, 'value': site})
    return options



# Create a dash application
app = dash.Dash(__name__)


 
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                html.Div([html.Label('Select Site : ') , dcc.Dropdown(options=get_sites_options(), value='all', id="site-dropdown")]
                                    , style={"marginRight":"40px", "marginLeft":"40px"}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',min=0, max=9000, step=1000, marks={0:'0', 100:'100'}, value=[min_payload, max_payload]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
# pie chart plot 
def get_pie_chart(site):
    if site == 'all':
        fig = px.pie(spacex_df, names="Launch Site", values='class')
    else :
        data_pie = spacex_df[spacex_df['Launch Site'] == site]
        data_pie = data_pie[['Launch Site','class']].groupby(['class']).count().reset_index()
        data_pie['result'] = data_pie['class']
        data_pie['result'].replace(to_replace=[0,1], value=['Failed', 'Successe'], inplace=True)
        fig = px.pie(data_pie, names='result', values='Launch Site', color_discrete_map={"Successe": '#45c566', "Failed": "red"}, color="result")
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='payload-slider',component_property='value')
)
def get_scatter_plot(values):
    data_scatter = spacex_df[spacex_df['Payload Mass (kg)'].between(values[0], values[1])]
    fig = px.scatter(data_scatter, x="Payload Mass (kg)", y="Launch Site" ,color="Mission Outcome")
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
