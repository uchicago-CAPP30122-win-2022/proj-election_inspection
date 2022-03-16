import dash
import dash_leaflet.express as dlx
from dash import html, dcc, dash_table
import folium as fl
import geopandas as gpd
import dash_bootstrap_components as dbc
import json
import requests
from dash.exceptions import PreventUpdate

def run_dash():
    district_data = gpd.read_file("election_inspection/visual_analysis/birch.geojson") #initial map
    red_district_data = district_data.iloc[:,2:8] #initial table

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])
    app.layout = html.Div([
                    dbc.Row(
                            dbc.Col(html.H1('Proposed Michigan Re-districting Map Demographics'), 
                                    style={'background-color':'#e6e6ff'})),
                    dbc.Row([
                        dbc.Col(html.Label(['Map Version:'], 
                                style={'font-weight': 'bold', "text-align": "center"}), 
                                width=1),
                        dbc.Col(dcc.Dropdown(id='map_version', 
                                            options=['apple', 'birch', 'chestnut', 'lange', 'szetela'],\
                                            value = 'birch'), 
                                width=2),
                        dbc.Col(html.Label(['District Statistics:'], 
                                            style={'font-weight': 'bold', "text-align": "center"}), 
                                width=1),
                        dbc.Col(dcc.Dropdown(id='stats', 
                                            options=[{'label': i, 'value': i} for i in red_district_data.columns], 
                                            value = 'PREDICTED_TURNOUT', 
                                            placeholder='Filter by demographic stats...'), 
                                width=4),
                        dbc.Col(html.Label(['Reveal VTDs?'], 
                                            style={'font-weight': 'bold', "text-align": "center"}),
                                width=1),
                        dbc.Col(dcc.Checklist([{"label":"Yes", "value":True}], 
                                            id = 'checkbox'), 
                                width=1)
                        ], 
                        style={'background-color':'#9999ff'}, 
                        align='center'),
                    dbc.Row([
                        dbc.Col(html.Iframe(id = 'map', 
                                            srcDoc = None, 
                                            height=500, 
                                            width='100%'), 
                                width=8),
                        dbc.Col(dash_table.DataTable(red_district_data.to_dict('records'), #initial file records to be replaced by callback
                                                    [{"name": i, "id": i} for i in red_district_data.columns], #inital file columns
                                                    id = 'tbl',
                                                    sort_action = 'native',
                                                    style_as_list_view = True,
                                                    style_cell = {'maxWidth':0, 'text-align':'center'},
                                                    style_header = {'backgroundColor': '#A7C3FE', 'fontWeight': 'bold', 'text-align':'center'},
                                                    row_selectable = 'single'
                                                    ),
                            width=4)
                        ],
                        className='g-0'),
                    dbc.Row([
                        dbc.Col(dcc.Markdown("""## Select a district in the table above for U.S. Representative information!""", id='info'))
                        ],
                        style={'background-color':'#e6f3ff'}, align='center')
                    ])

    @app.callback(dash.dependencies.Output('map', 'srcDoc'), 
                [dash.dependencies.Input('stats', 'value')], 
                [dash.dependencies.Input('map_version', 'value')],
                [dash.dependencies.Input('checkbox', 'value')])
    def recreate_map(attr, map, show_vtd):
        district_data = gpd.read_file(f"election_inspection/visual_analysis/{map}.geojson") #file path to new map
        m = fl.Map(location=[44.6, -84.563], 
                zoom_start=6,
                min_zoom = 6, 
                max_zoom = 15
                )
        district_tt = fl.GeoJsonTooltip(fields=['DISTRICTN', attr], aliases=['District:', attr + ':'])
        style = {
            'color': 'black',
            'weight': 2,
            'fillColor': 'grey', 
            'fillOpacity': 0.0}
        highlightStyle = {
            'color': 'red',
            'weight': 2,
            'fillColor': 'grey',
            'fillOpacity': 0.1
            }
        geojson = fl.GeoJson(
            data=district_data,
            name="district geojson",
            tooltip=district_tt,
            highlight_function = lambda x:highlightStyle,
            style_function = lambda x:style,
            zoom_on_click=True,)
        geojson.add_to(m)

        if show_vtd:
            choro_data = gpd.read_file(f"election_inspection/visual_analysis/vtd.geojson") #VTD File
            key_var = 'GEOID20'
        else:
            choro_data = district_data
            key_var = 'DISTRICTN'
        choro = fl.Choropleth(geo_data = choro_data, 
                        data = choro_data,
                        name="district choro", 
                        columns = [key_var, attr],
                        key_on = f'feature.properties.{key_var}', 
                        legend_name = attr)
        choro.add_to(m)
        m.keep_in_front(geojson)
        m.save('district_map.html')
        return open('election_inspection/visual_analysis/district_map.html', 'r').read()

    @app.callback(dash.dependencies.Output('tbl', 'data'), 
                [dash.dependencies.Input('map_version', 'value')])
    def recreate_table(map):
        district_data = gpd.read_file(f"election_inspection/visual_analysis/{map}.geojson") #path to new map file
        red_district_data = district_data.iloc[:,2:8]
        return red_district_data.to_dict('records')

    @app.callback(dash.dependencies.Output('info', 'children'), 
                [dash.dependencies.Input('tbl', 'selected_rows')])
    def us_rep_info(dist_list):
        if not dist_list:
            raise PreventUpdate
        dist_idx = dist_list[0]
        dist = red_district_data.iloc[dist_idx]['DISTRICTN']
        request_api = requests.get(f"""https://civicinfo.googleapis.com/civicinfo/v2/representatives/ocd-division%2Fcountry%3Aus%2Fstate%3Ami%2Fcd%3A{int(dist)}?levels=country&roles=legislatorLowerBody&key=AIzaSyDfMv-vUFL7qBsn6zoGlh4K6K1nIiSwQho""")
        rep_dict = json.loads(request_api.text)
        
        body_text = f"""
                    # {rep_dict['offices'][0]['name']} for {rep_dict['divisions'][f'ocd-division/country:us/state:mi/cd:{int(dist)}']['name']}
                    ## {rep_dict['officials'][0]['name']}
                    ### Party: {rep_dict['officials'][0]['party']}
                    Address: {rep_dict['officials'][0]['address'][0]['line1']} {rep_dict['officials'][0]['address'][0]['city']}, {rep_dict['officials'][0]['address'][0]['state']} {rep_dict['officials'][0]['address'][0]['zip']} \n
                    Phone:   {rep_dict['officials'][0]['phones'][0]} \n
                    Website: {rep_dict['officials'][0]['urls'][0]} 
                    """
        return body_text

if __name__ == '__main__':
    app.run_server(debug=True)