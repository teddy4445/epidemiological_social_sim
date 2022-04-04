# library imports
import os
import pandas as pd
import seaborn as sns
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
        data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "paper_main_plot_data.csv"))
        try:
            data.drop(['Unnamed: 0'], axis=1, inplace=True)
        except:
            pass
        for influance_times in list(data["influance_times"].unique()):
            for influance_amount in list(data["influance_amount"].unique()):
                for predicted_delay_weeks in list(data["predicted_delay_weeks"].unique()):
                    # prepare dataset for this plot
                    working_data = data[data["influance_times"] == influance_times]
                    working_data = working_data[working_data["influance_amount"] == influance_amount]
                    working_data = working_data[working_data["predicted_delay_weeks"] == predicted_delay_weeks]
                    working_data.drop(["influance_times", "influance_amount", "predicted_delay_weeks"], axis=1, inplace=True)
                    working_data = working_data.pivot("strategy", "policy", "mean_reduced_r_zero")
                    sns.heatmap(working_data,
                                cmap="coolwarm",
                                vmin=0,
                                vmax=0.6,
                                linewidths=.5)
                    plt.xlabel("")
                    plt.ylabel("")
                    plt.tight_layout()
                    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "heatmaps", "it-{}_ia-{}_pd-{}_heatmap.png".format(influance_times,influance_amount,predicted_delay_weeks))
                    plt.savefig(path, dpi=400)
                    plt.close()
                    print(path)


if __name__ == '__main__':
    MapPlot.plot_epi_data()
