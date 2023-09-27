
import base64
from csv import excel
import io
from time import process_time
from turtle import width
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
from dash import Dash, html, dcc, callback, Output, Input
from pandas import DataFrame, read_csv, read_excel, to_datetime
from .extractor import extract_who, process_data
from covid_space_time_analysis.models import covidAnalysis
external_stylesheets = [dbc.themes.LUMEN]

app = DjangoDash('Dashboard', external_stylesheets=external_stylesheets)
data = covidAnalysis()

# App layout
app.layout = dbc.Container(
    [
        

        dbc.Row(
            [
                html.Div(
                    "Space Time analysis of Covid-19",
                    className="text-center fs-1",
                    style={"color": "red", "font-weight": "bold"},
                )
            ]
        ),
        
        dbc.Row(
            [
                dbc.Card([
                    dbc.RadioItems(
                        options=[{"label": x, "value": x} for x in ["cases", "deaths"]],
                        value="deaths",
                        inline=True,
                        id="radio-buttons-final",
                        className="text-center font-weight-bold",
                        style={"font-size": "1.5 rem"},
                    )   
                ]),
                
                
            ],
        ),
        dcc.Loading(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dbc.Col([
                                        dbc.Button('Load',id='reloadWHO',class_name='bg-dark')
                                    ],width=1),
                                    dbc.Col([
                                    
                                    dcc.DatePickerRange(
                                        
                                        start_date=data.who_dataset["date"].min(),
                                        end_date=data.who_dataset["date"].max(),
                                        min_date_allowed=data.who_dataset["date"].min(),
                                        max_date_allowed=data.who_dataset["date"].max(),
                                        id="time_range",
                                        style={"font-size": "1.3 rem",'border':'2px solid black',},
                                    )],
                                    class_name='text-left',
                                    width=4
                                    ),
                                    dbc.Col([
                                        
                                        dbc.Card([
                                            dbc.Checklist([
                                                    {'label':'Bubble','value':True}],
                                                    value=[],
                                                    switch=True,
                                                    id='bubble-toggle')
                                        
                                    ])
                                            ],width=2,
                                    ),
                                    
                                    dbc.Col([
                                                
                                        dbc.Card([dbc.Checklist([
                                            {'label':'Per Millions','value':True}],
                                            value=[],
                                            switch=True,
                                            id='million-toggle')])
                                    ],width=2
                                    ),
                                    
                                        
                                            dbc.Col([
                                                dbc.Card([dbc.Checklist([
                                                    {'label':'Animate','value':True}],
                                                    value=[],
                                                    switch=True,
                                                    id='animate-toggle')])
                                    ],width=2
                                    )
                                
                                ]
                            ,className='d-flex align-items-center'
                            ),
                            dbc.Row(
                                [
                                dbc.Col(
                                    dbc.Card(dcc.Markdown(['# **Death:** '],id='death-count'),style={'color':'red'})
                                ),    
                                dbc.Col(
                                    dbc.Card(dcc.Markdown(['# **Cases:** '],id='cases-count'),style={'color':'green'})
                                ),
                                ]),
                            dbc.Card(
                                    [
                                    dcc.Graph(figure={}, id="chloropleth-plot",style={'height':'80vh'}),
                                    ]),
                            dcc.Dropdown(
                                id="country",
                                options=[i for i in data.who_dataset["Country"].unique()]
                                + ["global"],
                                searchable=True,
                                value="global",
                                multi=True,
                                className="text-center font-weight-bold",
                                style={
                                    "font-size": "1.5 rem",
                                    # 'color':'white',
                                    # 'background-color':'black'
                                    
                                },)
                        
                        ],
                        width=8,
                        className="font-weight-bold",
                        
                    ),
                    dbc.Col([
                        dbc.RadioItems(
                            options=[{"label": x, "value": x} for x in ['daily','monthly','weekly']],
                            inline=True,
                            value='daily',
                            id="interval-radio",
                            className="text-center font-weight-bold",
                            style={"font-size": "1.5 rem"},
                            ),
                        dbc.Card([dcc.Graph(figure={}, id="line-cum-plot")]),
                        dbc.Card([dcc.Graph(figure={}, id="line-daily-plot")])
                        ],width=4
                            ),
                ],
            ),

        type='cube'
    ),

    ],

    fluid=True,
)



# Add controls to build the interaction
@app.callback(
    Output(component_id="chloropleth-plot", component_property="figure"),
    Output(component_id="line-cum-plot", component_property="figure"),
    Output(component_id="line-daily-plot", component_property="figure"),
    
    Output(component_id="death-count", component_property="children"),
    Output(component_id="cases-count", component_property="children"),
    
    Output(component_id='reloadWHO',component_property='n_clicks'),
    
    Input(component_id="radio-buttons-final", component_property="value"),
    Input(component_id="time_range", component_property="start_date"),
    Input(component_id="time_range", component_property="end_date"),
    
    Input(component_id="country", component_property="value"),
    
    Input(component_id='interval-radio',component_property="value"),
    
    Input(component_id='bubble-toggle',component_property="value"),
    Input(component_id='million-toggle',component_property="value"),
    Input(component_id='animate-toggle',component_property="value"),
    Input(component_id='reloadWHO',component_property='n_clicks'),
    
    
)
def update_graph(Of, start_date, end_date, country,interval,bubble,million,animate,n_clicks):
    
    data = covidAnalysis()

    if n_clicks:
        extract_who().to_csv('who.csv')
        data=covidAnalysis()
            
    fig_chloro,df = data.make_chloro(        
        From=to_datetime(start_date), 
        Till=to_datetime(end_date), 
        Of=Of, 
        region=country,
        bubble=bool(bubble.__len__()),
        animate=bool(len(animate)),
        million=bool(million.__len__(),
        )
    )
    
    fig_cum_line,_ = data.make_timeseries(
        From=to_datetime(start_date), 
        Till=to_datetime(end_date), 
        Of=Of, 
        region=country
        ,interval=interval,
        million=bool(million.__len__()),
        
    )
    fig_daily_line,_ = data.make_timeseries(
        From=to_datetime(start_date),
        Till=to_datetime(end_date),
        Of=Of,
        cumulative=False,
        region=country,
        interval=interval,
        million=bool(million.__len__()),
        
    )
    deaths=f" # **Deaths {'per Million' if million else ''}: {round(df['deaths'].sum(),4)}**"
    cases=f" # **Cases {'per Million' if million else ''}: {round(df['cases'].sum(),4)}**"
    
    return fig_chloro, fig_cum_line, fig_daily_line,deaths, cases, 0,

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=8060)
