# library imports
import os
import pandas as pd
import geoplot as gplt
import geopandas as gpd
import mapclassify as mc
import matplotlib.pyplot as plt

# project imports


class MapPlot:
    """
    Map view of the data for the paper
    """

    def __init__(self):
        pass

    @staticmethod
    def plot_epi_data():
        # Read file
        epi_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "us-states.csv"))
        # extract the max cases per country
        idx = epi_data.groupby(['state'])['cases'].transform(max) == epi_data['cases']
        epi_data = epi_data[idx]
        # remove unwanted data
        epi_data.drop(["fips", "date", "deaths"], axis=1, inplace=True)
        epi_data.set_index("state", inplace=True)
        # load population size in each state
        pop_size_data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "us-states-size.csv"))
        pop_size_data.set_index("state", inplace=True)
        # merge data
        full_epi_data = pd.merge(epi_data, pop_size_data, left_index=True, right_index=True)
        full_epi_data.drop_duplicates(inplace=True)
        full_epi_data["infected_rate"] = 100*full_epi_data["cases"]/full_epi_data["pop_size"]
        # we do not need the raw data later
        full_epi_data.drop(["cases", "pop_size"], axis=1, inplace=True)
        full_epi_data.reset_index(inplace=True)
        # Load the json file with county coordinates
        geoData = gpd.read_file(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "us_map", "usa-states-census-2014.shp"))
        # merge spatial and temporal
        fullData = geoData.merge(full_epi_data, left_on=['name'], right_on=['state'])
        # print the map
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        # Set up the color sheme:
        scheme = mc.Quantiles(fullData['infected_rate'], k=10)
        # Map
        gplt.choropleth(fullData,
                        hue="rate",
                        linewidth=.1,
                        scheme=scheme,
                        cmap='coolwarm',
                        legend=True,
                        edgecolor='black',
                        ax=ax
                        )
        fig.tight_layout()
        plt.savefig(os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "epi_map.png"), dpi=600)
        plt.close()


if __name__ == '__main__':
    MapPlot.plot_epi_data()
