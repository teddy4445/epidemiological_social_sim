# library imports
import os
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
    Y_COL_NAME = "infected"
    # END - CONSTS #

    def __init__(self,
                 prediction_delays: list = None):
        self._prediction_delays = prediction_delays if prediction_delays is not None else [7*i for i in range(1,5)]
        self.x = None
        self.y = None
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
        x, y = NextWavePredictor.prepare(x=socio_data,
                                         y=epi_data[NextWave.Y_COL_NAME],
                                         y_classify_function=self.y_classify_function)
        # plot data for later analysis
        Plotter.plot_wave_signal(x=x,
                                 y_signal=epi_data[NextWave.Y_COL_NAME],
                                 binary_y_signal=y,
                                 save_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "next_wave_prepared_data.png"))
        # return results
        self.x, self.y = x, y

    def fit(self):
        """
        Fit all the models with the needed delays and save the results of the analysis
        """
        # split to train and test

        # run for all delay sizes
        best_losses = []
        best_accuracy = []
        for delay in self._prediction_delays:
            self._models[delay] = NextWavePredictor.fit(x_train=,
                                                        y_train=)
            test_loss, test_acc = self._models[delay].test(x_test=,
                                                           y_test=)
            best_losses.append(test_loss)
            best_accuracy.append(test_acc)

    def y_classify_function(self,
                            y: pd.Series):
        """
        This function defines what is considered an event given a single signal
        """
        raise NotImplemented("")
