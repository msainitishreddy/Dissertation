from math import nan
from pandas import isna
from pycountry import countries
import country_converter as coco
import iso3166

def iso3_extreme(row):
    iso2 = row["Country_code"]
    c_name = row["Country"]
    iso3 = coco.convert(c_name, not_found=nan, to="ISO3")
    if isna(iso3):
        iso3 = coco.convert(iso2, not_found=nan, to="ISO3")
    if isna(iso3):
        try:
            iso3 = countries.lookup(iso2).alpha_3
        except LookupError:
            try:
                iso3 = countries.lookup(c_name).alpha_3
            except LookupError:
                iso3 = nan
    return iso3


def iso3_convert(data):
    if data["Country_code"] in iso3166.countries_by_alpha2:
        return iso3166.countries_by_alpha2[data["Country_code"]].alpha3
    elif data["Country"] in iso3166.countries_by_name:
        return iso3166.countries_by_name[data["Country"]].alpha3
    elif data["Country"] in iso3166.countries_by_apolitical_name:
        return iso3166.countries_by_apolitical_name[data["Country"]].alpha3
    elif data["Country"] in ["Bonaire", "Saba", "Sint Eustatius"]:
        return "BES"
    else:
        return iso3_extreme(data)

