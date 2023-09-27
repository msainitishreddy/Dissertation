from datetime import datetime
from typing import Literal, Union,List
from pandas import DataFrame, Timestamp, read_csv, to_datetime

from .extractor import extract_who


import plotly.express as px
class covidAnalysis:
    def __init__(self) -> None:
        self.who_dataset: DataFrame
        try:
            self.who_dataset = read_csv("who.csv", index_col=0)
            self.who_dataset["date"] = to_datetime(self.who_dataset["date"])
        except FileNotFoundError:
            self.who_dataset = extract_who()
            self.who_dataset.to_csv("who.csv")


    def make_chloro(
        self,
        From: Timestamp,
        Till: Timestamp = to_datetime(datetime.now()),
        Of: Literal["deaths", "cases"] = "deaths",
        region: Union[Literal["global"], List[str]] = "global",
        bubble:bool=False,
        million:bool=False,
        animate:bool=False
    ):
        df = self.who_dataset[
            (self.who_dataset["date"] >= From) & (self.who_dataset["date"] <= Till)
        ]
        df = df if region == "global" else df[df["Country"].isin(region)]

        df = df.groupby(["iso3", "Country"]).sum(numeric_only=True).reset_index() if not animate else df

        

        if million:

            df[Of]=df[Of].div(1000000)
            df[f"Cumulative_{Of}"]=df[f"Cumulative_{Of}"].div(1000000)
            
        
        if animate:
            
            df.set_index('date',inplace=True)
            df= df.groupby(['iso3','Country']).resample('M').sum(numeric_only=True).reset_index()
            Of=f"Cumulative_{Of}"
        
        print(df)
        if bubble:
            fig=px.scatter_geo(
                df,
                locations="iso3",
                color=Of,
                size=Of,
                hover_name="Country",
                projection='orthographic' if not animate else 'natural earth2',
                
                animation_frame="date"  if animate else None,
                animation_group='iso3' if animate else None
                )
            fig.update_layout(
                geo = dict(
                    showcountries=True,
                    landcolor = 'rgb(217, 217, 217)',

                    ),
                
                )
            
        else:

            fig = px.choropleth(
                df,
                locations="iso3",
                color=Of,
                hover_name="Country",
                basemap_visible=True,
                
                color_continuous_scale="reds",
                projection='orthographic' if not animate else 'natural earth2',
                
                animation_frame="date"  if animate else None,
                animation_group='iso3' if animate else None,
                
                template='plotly'
            )
            fig.update_layout(
                autosize=True,
            )

        fig.update_yaxes(automargin=True)

        return fig,df

    
    def make_timeseries(
        self,
        From: Timestamp,
        Till: Timestamp = to_datetime(datetime.now()),
        Of: Literal["deaths", "cases"] = "deaths",
        region: Union[Literal["global"], List[str]] = "global",
        cumulative=True,
        interval:Literal['Weekly','daily','monthly']='daily',
        million:bool=False
    ):
        df = self.who_dataset[
            (self.who_dataset["date"] >= From) & (self.who_dataset["date"] <= Till)
        ]
        
        df = df if region == "global" else df[df["Country"].isin(region)]


        # Handling Interval
        
        df.set_index('date',inplace=True)
        if interval=='Weekly':
            df= df.groupby(['iso3','Country']).resample('W').sum(numeric_only=True).reset_index()
            df['interval'] = df['date'].dt.to_period('W').apply(lambda r: f'{r.start_time.date()} to {r.end_time.date()}')
        
        elif interval == 'daily':
            df.reset_index(inplace=True)
            df['interval']=df['date']
        
        elif interval == 'monthly':
            df= df.groupby(['iso3','Country']).resample('M').sum(numeric_only=True).reset_index()
            
            df['interval'] = df['date'].dt.to_period('M').apply(lambda r: f'{r.start_time.date()} to {r.end_time.date()}')
            
        df = (
            df.groupby(["date"]).sum(numeric_only=True).reset_index()
            if region == "global"
            else df
        )
        
        col=('Cumulative_' if cumulative else '')+Of
        
        if million:
            df[col]=df[col].div(1000000)
        
        fig = px.line(
            df,
            x="date",
            y=f"Cumulative_{Of}" if cumulative else Of,
            color_discrete_sequence=['red'] if region=='global' else None,
            
            title=f"{' '.join(region)} {Of} Time Series Graph",
            
            hover_data=[Of,f'Cumulative_{Of}'],

            color=None if region == "global" else "Country",
        )
        fig.update_layout(
            
            autosize=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig,df

