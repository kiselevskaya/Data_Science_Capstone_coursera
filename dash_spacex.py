

# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
print(f'Min_payload: {min_payload}, max_payload: {max_payload}')

success_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index().sort_values(by='class', ascending=False)
sites = success_df['Launch Site'].values
options = [{'label': f'{site}', 'value': 'site'+str(i+1)} for i, site in enumerate(sites)]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                dcc.Dropdown(id='site-dropdown',
                                             # options=[{'label': 'All sites', 'value': 'ALL'}],
                                             options=[{'label': 'All sites', 'value': 'ALL'}]+options,
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={i: f'{i}' for i in range(0, 12500, 2500)},
                                                value=[min_payload, max_payload]
                                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


def payload_df(payload, label='ALL'):
    bottom_payload, top_payload = payload[0], payload[1]
    if label == 'ALL':
        output = spacex_df[(spacex_df['Payload Mass (kg)'] > bottom_payload) & (spacex_df['Payload Mass (kg)'] < top_payload)]
    else:
        df = spacex_df[spacex_df['Launch Site'] == label]
        output = df[(df['Payload Mass (kg)'] > bottom_payload) & (df['Payload Mass (kg)'] < top_payload)]
    return output


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    [Output(component_id='success-pie-chart', component_property='figure'),
     Output(component_id='success-payload-scatter-chart', component_property='figure'),
     ],
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')
     ]
)
def get_pie_chart(entered_site, payload):
    # filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches by Site')
        scatter_fig = px.scatter(payload_df(payload), x="Payload Mass (kg)", y='class', color='Booster Version Category')
        return [fig, scatter_fig]
    else:
        for site in options:
            print(site['label'], site['value'])
            if entered_site == site['value']:
                df = spacex_df[spacex_df['Launch Site'] == site['label']]
                fig = px.pie(df,
                             names='class',
                             title=f'Total Success Launches for site {site["label"]}')
                scatter_fig = px.scatter(payload_df(payload, site['label']), x="Payload Mass (kg)",
                                         y='class', color='Booster Version Category')
                return [fig, scatter_fig]


# Run the app
if __name__ == '__main__':
    app.run_server()
