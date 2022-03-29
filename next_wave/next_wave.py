# library imports
import os
import json
import numpy as np
import pandas as pd

# project imports
from next_wave.next_wave_predictor import NextWavePredictor
from plotter import Plotter


class NextWave:
    """
    A class responsible to the next wave models tranining, analysis, saving results and integrate with other processes in
    the simulator
    """

    # CONSTS #
    TRAIN_PORTION = 0.8
    Y_COL_NAME = "infected"
    # END - CONSTS #

    def __init__(self,
                 prediction_delays: list = None):
        self._prediction_delays = prediction_delays if prediction_delays is not None else [7*i for i in range(1,5)]
        self.x_train = None
        self.y_train = None
        self.x_test  = None
        self.y_test  = None
        self._models = {}

    def load_data(self,
                  social_path: str,
                  epidemiological_path: str):
        """
        Load the data needed to the model and prepare to train the models
        """
        # load data
        socio_data = pd.read_csv(social_path)
        epi_data = pd.read_csv(epidemiological_path)
        # prepare for the model
        x = NextWavePredictor.prepare(x=socio_data)
        y = epi_data[NextWave.Y_COL_NAME]
        # split the data
        self.x_train = x.iloc[:x.shape[1]*NextWave.TRAIN_PORTION,: ]
        self.x_test = x.iloc[x.shape[1]*NextWave.TRAIN_PORTION:,: ]
        self.y_train = y.iloc[:x.shape[1]*NextWave.TRAIN_PORTION,: ]
        self.y_test = y.iloc[x.shape[1]*NextWave.TRAIN_PORTION:,: ]
        # plot data for later analysis
        Plotter.plot_wave_signal(x=x,
                                 y_signal=y,
                                 binary_y_signal=NextWave.y_classify_function(y=y),
                                 save_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "next_wave_prepared_data.png"))

    def fit(self):
        """
        Fit all the models with the needed delays and save the results of the analysis
        """
        # split to train and test

        # run for all delay sizes
        accuracy_test = []
        for delay in self._prediction_delays:
            # train data
            self._models[delay] = NextWavePredictor()
            self._models[delay].fit(x_train=self.x_train,
                                    y_train=self.y_train)
            # test data
            test_acc = self._models[delay].score(x_test=self.x_test,
                                                 y_test=self.y_test)
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
        raise NotImplemented("")
