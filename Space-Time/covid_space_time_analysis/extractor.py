
from pandas import DataFrame, read_csv, to_datetime

from .helpers import iso3_convert

def extract_who():
    who = read_csv(r"https://covid19.who.int/WHO-COVID-19-global-data.csv")

    # convert object > datetime
    who["Date_reported"] = to_datetime(who["Date_reported"])

    # Dropping Unnecesary_data
    who.drop(["WHO_region"], axis=1)

    # convert iso2 > iso3
    country_wise_data = (
        who.groupby(["Country", "Country_code"], dropna=False)
        .sum(True)[["New_deaths", "New_cases"]]
        .sort_values(ascending=False, by="New_deaths")
        .reset_index()
    )
    country_wise_data["iso3"] = country_wise_data.apply(iso3_convert, axis=1)
    cname_iso3 = {row["Country"]: row["iso3"] for row in country_wise_data.iloc}

    who["iso3"] = who["Country"].map(cname_iso3)

    # merge some miscellenius countries that is internationally assigned same iso value

    who.rename(
        {
            "Country_code": "iso2",
            "New_deaths": "deaths",
            "New_cases": "cases",
            "Date_reported": "date",
        },
        axis=1,
        inplace=True,
    )
    who['deaths'] = abs(who['deaths'])
    # filter out only the required data and store it
    return who

    # TODO: Make chloropleth graph based on selected date range


def process_data(df:DataFrame):
    df['date']=to_datetime(df['date'])
    if 'iso3' not in df.columns:
        if 'iso2' in df.columns:
            df.rename({'iso2','Country_code'},inplace=True,axis=1)
        
        
            # convert iso2 > iso3
        country_wise_data = (
            df.groupby(["Country", "Country_code"], dropna=False)
            .sum(True)[["deaths", "cases"]]
            .sort_values(ascending=False, by="deaths")
            .reset_index()
        )
        country_wise_data["iso3"] = country_wise_data.apply(iso3_convert, axis=1)
        cname_iso3 = {row["Country"]: row["iso3"] for row in country_wise_data.iloc}

        df["iso3"] = df["Country"].map(cname_iso3)        
    
    df.set_index('date',inplace=True)
    df.sort_index(inplace=True)
    
    df['Cumulative_deaths']=df['deaths'].cumsum()
    df['Cumulative_cases']=df['cases'].cumsum()
        
    return df