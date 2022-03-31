# library imports
import os
import json
import pandas as pd
import scipy.stats as stats

# project imports
from plotter import Plotter
from next_wave.next_wave_predictor import NextWavePredictor


class NextWaveManager:
    """
    A class responsible to the next wave models tranining, analysis, saving results and integrate with other processes in
    the simulator
    """

    # CONSTS #
    TRAIN_PORTION = 0.9
    Y_COL_NAME = "cases"
    # END - CONSTS #

    def __init__(self,
                 prediction_delays: list = None):
        self._prediction_delays = prediction_delays if prediction_delays is not None else [7*i for i in range(0,5)]
        self.data = None
        self._models = {}

    def load_data(self,
                  path_or_df: str):
        """
        Load the data needed to the model and prepare to train the models
        """
        # load data
        if isinstance(path_or_df, str):
            data = pd.read_csv(path_or_df)
        elif isinstance(path_or_df, pd.DataFrame):
            data = path_or_df
        else:
            raise Exception("Error at NextWaveManager.load_data: not support argument type '{}'".format(type(path_or_df)))
        # prepare for the model
        x = NextWavePredictor.prepare(x=data.drop([NextWaveManager.Y_COL_NAME], axis=1, inplace=False))
        y = pd.Series(stats.zscore(data[NextWaveManager.Y_COL_NAME]))
        self.data = x.copy()
        self.data["y_delayed"] = y
        # plot data for later analysis
        Plotter.plot_wave_signal(x=x,
                                 y_signal=y,
                                 binary_y_signal=NextWaveManager.y_classify_function(y=y),
                                 smooth=False,
                                 save_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "next_wave_prepared_data.png"))
        Plotter.plot_wave_signal(x=x,
                                 y_signal=y,
                                 binary_y_signal=NextWaveManager.y_classify_function(y=y),
                                 smooth=True,
                                 save_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "smoothed_next_wave_prepared_data.png"))

    def fit(self):
        """
        Fit all the models with the needed delays and save the results of the analysis
        """
        # run for all delay sizes
        accuracy_test = []
        for delay in self._prediction_delays:
            df = NextWavePredictor.series_to_supervised(df=self.data,
                                                        n_in=14,
                                                        n_out=delay,
                                                        dropnan=True)
            x = df.drop(["y"], axis=1)
            y = df["y"]
            x_train = x.iloc[:round(x.shape[0] * NextWaveManager.TRAIN_PORTION), :]
            x_test = x.iloc[round(x.shape[0] * NextWaveManager.TRAIN_PORTION):, :]
            y_train = y.iloc[:round(y.shape[0] * NextWaveManager.TRAIN_PORTION)]
            y_test = y.iloc[round(y.shape[0] * NextWaveManager.TRAIN_PORTION):]
            # train data
            self._models[delay] = NextWavePredictor(prediction_delay=delay)
            self._models[delay].fit(x_train=x_train,
                                    y_train=y_train)
            # test data
            test_acc = self._models[delay].score(x_test=x_test,
                                                 y_test=y_test)
            # recall results
            accuracy_test.append(test_acc)
        # show the results o
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "fit_results.json"), "w") as next_wave_file:
            json.dump({"delays": self._prediction_delays,
                       "accuracy": accuracy_test},
                      next_wave_file)

    @staticmethod
    def y_classify_function(y: pd.Series):
        """
        This function defines what is considered an event given a single signal
        """
        answer = [1 if y.iloc[index+1] > y.iloc[index] else 0 for index in range(len(y)-1)]
        answer.append(0)
        return pd.Series(answer)
